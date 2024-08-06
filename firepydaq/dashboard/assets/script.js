// var metaTag = document.querySelector('meta[name="viewport"]');
//     if (metaTag) {
//         console.log(metaTag.getAttribute('content'))
//         console.log("Found")
//         metaTag.content = 'width=device-width, initial-scale=1.0'
//     } 
// console.log("Logged")

document.addEventListener('DOMContentLoaded', function() {
    const viewport = document.querySelector('meta[name="viewport"]');
    if (viewport) {
        console.log(viewport.getAttribute('content'))
        } else {
        console.log('Not found')
    }
})