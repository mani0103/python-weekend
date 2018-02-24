from flask import request, jsonify, app, Flask
from connections import search_for_connections

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

@app.route('/search', methods=['GET'])
def search():
  date = request.args.get('date')
  src = request.args.get('src')
  dst = request.args.get('dst')

  results = search_for_connections(src, dst, date)

  return jsonify(results)

if __name__ == '__main__':
   app.run()

