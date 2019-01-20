const uploadPlace = document.querySelector('#upload-place');
const imageCanvas = document.querySelector('#imageCanvas');

uploadPlace.addEventListener('sumbmit', (e)=> {
    e.preventDefault();
})

var uploadPlaceDropZone = new Dropzone("#upload-place", { 
    url: "/file/post"
});


uploadPlaceDropZone.on("addedfile", function(file) {    
});

uploadPlaceDropZone.on("thumbnail", function(file) {
    aspect = file.height / file.width;
    width = 400;
    height = width * aspect;
    uploadPlace.style;
    
    Object.assign(uploadPlace.style, {
        backgroundImage: `url(${file.dataURL})`,
        backgroundSize: 'contain',
        width: `${width}px`,
        height: `${height}px`
    });


    preview = document.querySelector('#preview');
    preview.src = file.dataURL;
    let src = cv.imread(preview);
    let dst = src.clone()
    // let dst = cv.Mat.zeros(src.cols, src.rows, cv.CV_8UC3);
    cv.cvtColor(src, src, cv.COLOR_RGBA2GRAY, 0);
    cv.threshold(src, src, 120, 200, cv.THRESH_BINARY);
    let contours = new cv.MatVector();
    let hierarchy = new cv.Mat();
    // You can try more different parameters
    cv.findContours(src, contours, hierarchy, cv.RETR_CCOMP, cv.CHAIN_APPROX_SIMPLE);
    // draw contours with random Scalar
    let color = new cv.Scalar(255, 0, 0, 255);
    for (let i = 0; i < contours.size(); ++i) {
        area = cv.contourArea(contours.get(i), false);
        console.log(area)
        if (area <= 50 && area >= 30)
            cv.drawContours(dst, contours, i, color, 1, cv.LINE_8, hierarchy, 100);
    }
    cv.imshow('imageCanvas', dst);
    src.delete(); dst.delete(); contours.delete(); hierarchy.delete();
    
});

function onOpenCvReady() {
    console.log("onOpenCvReady")
}