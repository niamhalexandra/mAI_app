from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
# Serve the HTML page
@app.route('/')
def index():
    return render_template('index.html')

# Endpoint to receive spoken and convert text
@app.route('/transcribe', methods=['POST'])
def transcribe():
    data = request.json
    transcription = data.get('transcription')
    print(f"Received transcription: {transcription}")
    
    # You can save or process the transcription here.
    # For example, you could write it to a file:
    #with open("transcription.txt", "a") as file:
        #file.write(transcription + "\n")
    
    # Return a JSON response
    return jsonify({"status": "success", "transcription": transcription})

if __name__ == '__main__':
    app.run(debug=True)






