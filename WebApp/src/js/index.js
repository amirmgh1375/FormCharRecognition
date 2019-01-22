const uploadPlace = document.querySelector('#upload-place');
const imageCanvas = document.querySelector('#imageCanvas');

//  Disabling the dropzone default upload behaiviour (FIXME:)
uploadPlace.addEventListener('sumbmit', (e)=> {
    e.preventDefault();
})

// Creating a Dropzone element
var uploadPlaceDropZone = new Dropzone('#upload-place', { 
    url: '/predict'
});

// After a File is selected (image might not be read yet)
uploadPlaceDropZone.on('addedfile', function(file) {    
});

// After selected image is read and the data URL is ready
uploadPlaceDropZone.on('thumbnail', function(file) {
    // Disable dropzone on upload place so that clicking wont bring browse window
    uploadPlaceDropZone.disable();

    // Get image preview canvas context
    ctx = imageCanvas.getContext('2d');
    // Create an image and add selected images data url
    var imageObj = new Image();
    imageObj.src = file.dataURL;
    // After data url is added to image, draw it on convas
    imageObj.onload = function() {
        // calculate a Suitable size for resizing image
        // (Image might be too big)
        aspect =  file.width / file.height;
        height = 600;
        width = height * aspect;
        
        Object.assign(uploadPlace.style, {
            width: `${width}px`,
            height: `${height}px`
        });

        console.log(width, height);
        
        
        imageCanvas.style.display = 'block';
        imageCanvas.width = width;
        imageCanvas.height = height;

    
        ctx.drawImage(imageObj, 0, 0, file.width, file.height, 0, 0, width, height);

        setTimeout(() => {
            drawContoures(imageCanvas);
        }, 500);
    };
});

function onOpenCvReady() {
    console.log('onOpenCvReady')
}

function drawContoures(canvas) {
    let src = cv.imread(canvas);
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
        if (area <= 130 && area >= 100){
            console.log(area, cv.boundingRect(contours.get(i)))
            cv.drawContours(dst, contours, i, color, 1, cv.LINE_8, hierarchy, 100);
        }
    }
    cv.imshow('imageCanvas', dst);
    src.delete(); dst.delete(); contours.delete(); hierarchy.delete();
}