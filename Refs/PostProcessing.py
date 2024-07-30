#######################
## This script will first post processes experiment data by scaling them into respective units in real time ##
## Then, this will produce custom data fields based on predefined formulae in the formulae file ##
## All processed data will be saved in the same location as the experimental data
## By: Dushyant M. Chaudhari ##
## Updated: June 20, 2024 #####
#######################

import polars as pl
import re
import numpy as np
import sys
import pyarrow.parquet as pq # Try to read groups of rows for potentially faster updates

class PostProcessData():
	def __init__(self, formulae_file) -> None:
		'''
		Any key in Formulae_dict found in the equation will be replaced by the corresponding item
		'''
		self.Formulae_dict = {"sqrt":"np.sqrt",
							"pi":"np.pi",
							"mean":"np.mean",
							"max":"max",
							"abs":"np.abs"}
		self.Errors = {} # Empty error dict. Any errors will be saved in the log file

		self.df,self.fpath,self.df_config,self.configpath = self.initialize_Data()
		self.ScaleData()
		# print(self.df_processed.head(5),self.df_processed.columns)
		self.formulae_file = formulae_file
		self.ParseFormulae(self.formulae_file)
		self.MergeConfig_Formulae()
		# print(self.All_chart_info["Label"].to_list())
		# print(self.df_processed.columns)
		# print(self.df_processed.head(5),self.df_processed.columns)
		
	def MergeConfig_Formulae(self):
		select_cols = ["Label","Chart","Layout","Position","Processed_Unit","Legend"]
		config_info = self.df_config.select(select_cols)
		formulae_info = self.formulae_df.select(select_cols)
		All_chart_info = pl.concat([config_info,formulae_info])

		All_chart_info = All_chart_info.filter(~pl.col("Chart").str.contains("Intermediate"))
		All_chart_info = All_chart_info.filter(~pl.col("Chart").str.contains("Constant"))
		self.All_chart_info = All_chart_info
		self.All_chart_info.rename(str.strip).columns
		self.All_chart_info = self.All_chart_info.with_columns(pl.col(pl.Utf8).str.strip_chars())
		

	def initialize_Data(self,file ="DAQsavefilepath.txt"):
		with open(file,'r') as f:
			lines = f.readlines()
		fpath = lines[0].strip()
		# print(fpath)
		configpath = lines[1].strip()

		df = pl.read_parquet(fpath)
		# print(df.head(5))
		df_config = pl.read_csv(configpath)
		return df,fpath,df_config,configpath

	def UpdateData(self, save_path):
		self.df = pl.read_parquet(self.fpath)
		self.ScaleData()
		self.ParseFormulae(self.formulae_file)
		self.df_processed.write_parquet(save_path.strip('.parquet')+'_PostProcessed.parquet')

	def ScaleData(self):
		self.df_processed = pl.DataFrame()
		for col in self.df.columns:
			if "Absolute_Time" not in col:
				self.df = self.df.cast({col:pl.Float32})
			if "Time" in col:
				self.df_processed = self.df_processed.with_columns(pl.Series(self.df.select(col)).alias(col))
			elif not self.df_config.filter(pl.col("Type")=="Thermocouple").filter(pl.col("Label")==col).is_empty():
				self.df_processed = self.df_processed.with_columns(pl.Series(self.df.select(col)).alias(col))
			else:
				try:
					local_scales = self.df_config.filter(pl.col("Label")==col)
					min_AI = local_scales.select("AIRangeMin").item()
					unit_per_V = ((local_scales.select("ScaleMax") - local_scales.select("ScaleMin"))/(local_scales.select("AIRangeMax") - local_scales.select("AIRangeMin"))).item()
					offset = local_scales.select("ScaleMin").item()
					# print(unit_per_V,offset)
					self.df_processed = self.df_processed.with_columns((pl.Series((self.df.select(pl.col(col).abs())-min_AI)*unit_per_V+offset)).alias(col))
				except ValueError:
					self.df_processed = self.df_processed.with_columns(pl.Series(self.df.select(col)).alias(col))

	def CheckVarMacthes(self,var,rhs,replacement):
		# Look for variable with non alphanumeric, and underscore characters before or after the string. i.e. a-zA-Z0-9_
		pattern = r"(?<![\w])"+var+r"(?![\w])" 
		matcher = re.finditer(pattern,rhs,re.IGNORECASE)
		matchy_spans = [(re.findall(var,i.group())[0],i.span()) for i in matcher]
		for i in range(len(matchy_spans)):
			matches = matchy_spans[i]
			rhs = rhs[:matches[1][0]] + replacement + rhs[matches[1][1]:]
			
			# Updating the variable match based on given replacement string
			matcher = re.finditer(pattern,rhs,re.IGNORECASE)
			matchy_spans = [(i.group(),i.span()) for i in matcher]

		return rhs

	def ExecEqn(self,lhs,rhs):
		try:
			exec('setattr(self,lhs,eval(rhs))')
			return
		except:
			the_type, the_value, the_traceback = sys.exc_info()
			# print(the_value.__str__())
			if the_type == NameError:
				err_val = the_value.__str__()
			elif the_type == SyntaxError:
				err_val = the_value.text.split('=')[0]
			if not (lhs, err_val) in self.Errors:
				self.Errors[(lhs, err_val)] = str(the_type)
				print(lhs,the_type, ': ', err_val.strip())
			skip_processing = True
	
	def ParseFormulae(self, formulae_file):
		## Further Processing based on provided formulae
		
		self.formulae_df = pl.read_csv(formulae_file)
		for row in self.formulae_df.iter_rows(named=True):
			skip_processing = False
			lhs = row["Label"].strip()
			rhs = row["RHS"].strip()
			eqn = lhs + '=' + rhs
			if "Constant" in row["Chart"]:
				self.ExecEqn(lhs,rhs)
			else:
				# vars = re.findall(r'[A-Za-z]+_?[A-Za-z0-9]+',rhs)
				vars = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*',rhs)
				if vars == []: # Constant
					self.ExecEqn(lhs,rhs)
					# print('const?',lhs,getattr(self,lhs))
					continue
				unique_vars = pl.Series(vars).unique()
				all_var_counter = 0
				for var in unique_vars:
					processed_in_df = False
					if any([var in i for i in self.Formulae_dict.keys()]):
						continue
					if var in locals(): # Checking for Constants and Intermediates
						var_exists = True
						continue
					elif var not in locals() and hasattr(self,var):
						rhs = self.CheckVarMacthes(var,rhs,'getattr(self,\"'+var+'\")')
						continue
					try:
						# Checking for variable in the processed_df
						if not self.df_processed.select(var).is_empty(): 
							processed_in_df = True
							setattr(self,var, self.df_processed.select(var).to_numpy().flatten())
							rhs = self.CheckVarMacthes(var,rhs,'getattr(self,\"'+var+'\")')
						else:
							print("Variable " + var + ", does not exist in locals or in collected/processed data. Please check variables. Skipping with the processing")
							skip_processing = True
					except:
						the_type, the_value, the_traceback = sys.exc_info()
						err_val = the_value.__str__()
						if not (lhs, err_val) in self.Errors:
							self.Errors[(lhs, err_val)] = str(the_type)
							print(lhs,the_type, ': ', err_val.strip())
						skip_processing = True
				for i in self.Formulae_dict.keys(): # final replacement of formulae to python parseable functions
					if i in rhs:
						rhs = self.CheckVarMacthes(i,rhs,self.Formulae_dict[i])
				eqn = lhs + '=' + rhs

			if not skip_processing:
				# print(eqn)
				try:
					exec('setattr(self,lhs,eval(rhs))')
					if isinstance(getattr(self,lhs),np.ndarray) and ((row["Chart"]!="Intermediate") and (row["Chart"]!="Constant")):
						self.df_processed = self.df_processed.with_columns(pl.Series(getattr(self,lhs)).alias(lhs))
				except:
					the_type, the_value, the_traceback = sys.exc_info()
					err_val = the_value
					if the_type == NameError:
						err_val = the_value.__str__()
					elif the_type == SyntaxError:
						err_val = the_value.text.split('=')[0]
					if not (lhs, err_val) in self.Errors:
						self.Errors[(lhs, err_val)] = str(the_type)
						print(lhs,the_type, ': ', err_val.strip())
					skip_processing = True

				
		if self.Errors !=[]:
			with open('Errorlog_formulae.log','w') as f:
				for key,error_item in self.Errors.items():
					f.write(key[0] + " : " + key[1] + " :: " + error_item +'\n')

if __name__ == "__main__":
	import matplotlib.pyplot as plt
	import time
	formulae_file = "../ConfigFiles/Processing_formulae.csv"
	testing = PostProcessData(formulae_file)
	
	if "HRR_COCO2" in testing.df_processed.columns:
		plt.plot(testing.df_processed.select("Time"),testing.df_processed.select("HRR_COCO2"))
		plt.show()
	print(testing.df_processed.columns)
	for chart_type,chart_df in testing.All_chart_info.group_by(["Chart"]):
		if not chart_df.select("Label")[0].item() in testing.df_processed.columns:
			continue
		fig,axes = plt.subplots(chart_df.select("Layout")[0].item())
		if not isinstance(axes,np.ndarray): # If it is only a single axis
			axes = [axes]
		for row in chart_df.iter_rows(named=True):
			try:
				axes[row["Position"]-1].plot(testing.df_processed.select("Time"),testing.df_processed.select(row["Label"]),label=row["Legend"])
				axes[row["Position"]-1].set_xlabel("Time (s)")
				axes[row["Position"]-1].set_ylabel(row["Chart"]+" ( "+row["Processed_Unit"]+" )")
				axes[row["Position"]-1].legend()
			except:
				the_type, the_value, the_traceback = sys.exc_info()
				print(the_type, ': ', the_value)

	for i in range(1):
		t1 = time.time()
		save_path = ''
		testing.UpdateData(save_path)
		t2 = time.time()
		print("Time for processing :"+str(t2-t1))
	
	plt.show()


