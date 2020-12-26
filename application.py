from funnel import application

if __name__ == '__main__':
  port = 5001
  host = "127.0.0.1"
  application.run(host=host, port=port, threaded=True)
