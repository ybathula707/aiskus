from app.app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)


# This code is the entry point for the Flask application.
# It imports the Flask app instance from app.app and then runs the app, hosted on 0.0.0.0 on port 5001
# what does this mean?
"""
python run.py will start the Flask application from this entry point, making it accessible on all network interfaces of the host machine.

LAN: Local Area Network

All devices connected to the same network comprise the LAN,
When the application hosting is binded to network interface 0.0.0.0, this means that the application is
listening for incoming requests on all available network interfaces of the host machine, using the 
specified port number as the channel. 
In this away, the application becomes accessible to any device connected to the same LAN, 
using the the host's IP address and port number.

    ex: http://192.168.86.31:5001 ANY device on LAN can access the app using this URL


"""