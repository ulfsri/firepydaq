// // var metaTag = document.querySelector('meta[name="viewport"]');
// //     if (metaTag) {
// //         console.log(metaTag.getAttribute('content'))
// //         console.log("Found")
// //         metaTag.content = 'width=device-width, initial-scale=1.0'
// //     } 
// // console.log("Logged")

document.addEventListener('DOMContentLoaded', ()=> {
    console.log("MY File")
    const display_switch = document.getElementById('display-switch')
    console.log(display_switch)
    console.log("Found Switch")
    if (display_switch) {
        console.log("Found Switch")
        display_switch.addEventListener('value', function() {
            console.log("Changed")
        })
    }
})

