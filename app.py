from flask import Flask, render_template, request, redirect, url_for
import os
import cv2
import time

app = Flask(__name__)

# Ensure folders exist
UPLOAD_FOLDER = "uploads"
CARTOONIFIED_FOLDER = "static"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CARTOONIFIED_FOLDER, exist_ok=True)

@app.route("/")
def home():
    print(f"Templates folder exists: {os.path.exists('templates/index.html')}")
    return render_template("index.html")

@app.route("/cartoonify", methods=["POST"])
def cartoonify():
    file = request.files.get("file")
    if file:
        # Generate a unique filename
        timestamp = int(time.time())
        filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(UPLOAD_FOLDER, filename)

        # Save uploaded file
        file.save(file_path)

        try:
            # Read and process the image
            image = cv2.imread(file_path)
            if image is None:
                raise ValueError("Invalid image file")

            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            edges = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9
            )
            color = cv2.bilateralFilter(image, 9, 300, 300)
            cartoonified_image = cv2.bitwise_and(color, color, mask=edges)

            # Save cartoonified image
            cartoonified_filename = f"cartoonified_{filename}"
            cartoonified_path = os.path.join(CARTOONIFIED_FOLDER, cartoonified_filename)
            cv2.imwrite(cartoonified_path, cartoonified_image)

        except Exception as e:
            print(f"Error processing image: {e}")
            return redirect(url_for("home"))

        # Pass the cartoonified filename to the result template
        return render_template("result.html", filename=cartoonified_filename)

    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)