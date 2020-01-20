from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        print(request.form.getlist('hello'))

    return '''<form method="post">
<div>
<input type="checkbox" name="hello" value="world" checked>
<label for="hello">Subscribe to newsletter?</label>
</div>
<input type="checkbox" name="hello" value="davidism" checked>
<input type="submit">
</form>'''

app.run()
