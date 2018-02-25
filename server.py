from flask import request, jsonify, app, Flask, render_template
from connections import search_for_connections

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

@app.route("/")
def template_test():
    return render_template('template.html', data=[])

@app.route('/', methods=['POST'])
def my_form_post():
  date = request.form['date']
  src = request.form['from']
  dst = request.form['to']
  
  results = search_for_connections(src, dst, date)
  #print(type(results))
  return render_template('template.html', data=results)


@app.route('/search', methods=['GET'])
def search():
  date = request.args.get('date')
  src = request.args.get('src')
  dst = request.args.get('dst')


  results = search_for_connections(src, dst, date)
  print(type(results))
  return jsonify(results)

if __name__ == '__main__':
   app.run(debug=True)

