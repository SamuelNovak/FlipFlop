window.addEventListener("DOMContentLoaded", function() {
    var video = document.getElementById('video');
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        const getImage = async () => {
            video.srcObject = await navigator.mediaDevices.getUserMedia({ video: true })
            video.play();
        }
        getImage()
    }
    var message = document.getElementById('message');
    
    document.getElementById("reset-app").addEventListener("click", function() {
        var img = document.getElementById("result");
        var capture = document.getElementById("capture");
        var video = document.getElementById("video");
        var reset = document.getElementById("reset-app");
        var suggest = document.getElementById("suggestion");

        img.classList.add("d-none");
        reset.classList.add("d-none");
        suggest.classList.add("d-none");

        video.classList.remove("d-none");
        capture.classList.remove("d-none");
    });

    document.getElementById("suggestion").addEventListener("click", function() {
        window.open("suggestion.html?emotion=" + this.getAttribute("data-emotion"), "_blank").focus();
    });

    document.getElementById('capture').addEventListener('click', function() {
        var capture = document.getElementById("capture");
        capture.classList.add("d-none");
        var canvas = document.createElement('canvas');
        canvas.width = 640;
        canvas.height = 480;
        var context = canvas.getContext('2d');
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        var data = {
            'image_base64': canvas.toDataURL("image/png"),
            'emotion': '{{ page_data.emotion }}'
        }
        const getResult = async () => {
            var result = await fetch('face', {
                method: 'POST',
                body: JSON.stringify(data),
                headers: { 'Content-Type': 'application/json' }
            })
            var jsonResult = await result.json();
            console.log(jsonResult);
            console.log(jsonResult.status == "ok");
            if (jsonResult.status == "ok") {
                var img = document.getElementById("result");
                var video = document.getElementById("video");
                var reset = document.getElementById("reset-app");
                var suggest = document.getElementById("suggestion");

                img.setAttribute("src", jsonResult.image_base64);
                img.classList.remove("d-none");
                reset.classList.remove("d-none");
                
                suggest.classList.remove("d-none");
                suggest.textContent = "You seem ";
                if (jsonResult.emotion == "happiness")
                    suggest.textContent += "HAPPY today. ";
                else if (jsonResult.emotion == "neutral")
                    suggest.textContent += "QUITE ALRIGHT today. ";
                else if (jsonResult.emotion == "surprise")
                    suggest.textContent += "SURPRISED, is it a good or a bad surprise? "
                else
                    suggest.textContent += "UNHAPPY, hope we can cheer you up. "
                suggest.textContent += "Would you like a suggestion close to your location?"
                suggest.setAttribute("data-emotion", jsonResult.emotion);

                video.classList.add("d-none");
                capture.classList.add("d-none");
            } else {
                alert(jsonResult.message);
                capture.classList.remove("d-none");
            }
        }
        getResult()
    });
})