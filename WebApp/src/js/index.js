const uploadPlace = document.querySelector('#upload-place');
const imageCanvas = document.querySelector('#imageCanvas');

//  Disabling the dropzone default upload behaiviour (FIXME:)
uploadPlace.addEventListener('sumbmit', (e)=> {
    e.preventDefault();
})

// Creating a Dropzone element
var uploadPlaceDropZone = new Dropzone('#upload-place', { 
    url: '/file/post'
});

// After a File is selected (image might not be read yet)
uploadPlaceDropZone.on('addedfile', function(file) {    
});

// After selected image is read and the data URL is ready
uploadPlaceDropZone.on('thumbnail', function(file) {
    // Disable dropzone on upload place so that clicking wont bring browse window
    uploadPlaceDropZone.disable();

    preview = document.querySelector('#preview')
    preview.src = file.dataURL;

    // Get image preview canvas context
    ctx = imageCanvas.getContext('2d');
    // Create an image and add selected images data url
    // var imageObj = new Image();
    // imageObj.src = file.dataURL;
    // After data url is added to image, draw it on convas
    // imageObj.onload = function() {
    //     // calculate a Suitable size for resizing image
    //     // (Image might be too big)
    //     aspect = file.height / file.width;
    //     width = 400;
    //     height = width * aspect;

    //     console.log(imageObj.width);
    //     console.log(imageObj.height);
        

    
    //     ctx.drawImage(imageObj, 0, 0, imageObj.width, imageObj.height, 0, 0, width, height);
    // };
    Object.assign(uploadPlace.style, {
        width: `${file.width}px`,
        height: `${file.height}px`
    });
    imageCanvas.style.display = 'block';
    imageCanvas.width = file.width;
    imageCanvas.height = file.height;
    

    setTimeout(() => {
        console.log(imageCanvas.width);
        console.log(imageCanvas.height);
        ctx.drawImage(preview, 0, 0);
    }, 2000);


    


    // preview = document.querySelector('#preview');
    // preview.src = file.dataURL;
    // let src = cv.imread(preview);
    // let dst = src.clone()
    // // let dst = cv.Mat.zeros(src.cols, src.rows, cv.CV_8UC3);
    // cv.cvtColor(src, src, cv.COLOR_RGBA2GRAY, 0);
    // cv.threshold(src, src, 120, 200, cv.THRESH_BINARY);
    // let contours = new cv.MatVector();
    // let hierarchy = new cv.Mat();
    // // You can try more different parameters
    // cv.findContours(src, contours, hierarchy, cv.RETR_CCOMP, cv.CHAIN_APPROX_SIMPLE);
    // // draw contours with random Scalar
    // let color = new cv.Scalar(255, 0, 0, 255);
    // for (let i = 0; i < contours.size(); ++i) {
    //     area = cv.contourArea(contours.get(i), false);
    //     console.log(area)
    //     if (area <= 50 && area >= 30)
    //         cv.drawContours(dst, contours, i, color, 1, cv.LINE_8, hierarchy, 100);
    // }
    // cv.imshow('imageCanvas', dst);
    // src.delete(); dst.delete(); contours.delete(); hierarchy.delete();
    
});

function onOpenCvReady() {
    console.log('onOpenCvReady')
}