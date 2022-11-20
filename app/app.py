from flask import Flask, render_template, request, url_for, flash, redirect

app = Flask(__name__)
app.config['SECRET_KEY'] = '2fb00ba40abdb34f11c9026204333136a8afc9406e7e2f86'

messages = [{'title': 'Bitcoin AirBNB',
             'content': 'We are going to replace AirBNB with a better Bitcoin verison'},
            {'title': 'Message Two',
             'content': 'Message Two Content'}
            ]

if __name__ == "__main__":
    app.run()

@app.route('/', methods=(['GET', 'POST']))
def index():
    return render_template('index.html', messages=messages)

@app.route('/create/', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        print("REQUEST:", request)
        return redirect(url_for('index'))

        # if not title:
        #     flash('Title is required!')
        # elif not content:
        #     flash('Content is required!')
        # else:
        #     messages.append({'title': title, 'content': content})
        #     return redirect(url_for('index'))

    return render_template('create.html')
