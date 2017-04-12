# MTurk Starter Kit

This is a Flask app with Mechanical Turk integration, with the data stored on Firebase.
It comes with basic Heroku integration such that you can host it using the basic, free, 1-dyno machine.
The templating engine is based on Pug.


## Routes

Examples will be hosted at `/example/<example_id>?prod=<mechanical_turk_prod?>`.
When the server receives this request, it will pull in the example corresonding to `example_id` from Firebase and display `templates/example.pug` after populating it with the example.


## Firebase

To authenticate with Firebase, we use your app information from `config.json`.
Your database permission should be set to readable by everyone.
You should probably limit your write permission.

Examples are written to `/examples`, with the key being `example_id` and the payload being the json object corresponding to the example.


## MTurk

For Mechanical Turk, there are two "locations" we need to talk to - the sand box or the production server.
Because our server is not aware of who it is talking to, we will tell it about the source using a request parameter.
Namely, when a hit comes from production, it should have the query parameter `prod=True`.


## Deploying on Heroku

Run `heroku create` the first time.
After that, you should be able to push to production with `heroku push`.


# Managing Jobs on MTurk

The binaries in `./mturk` help you submit and manage jobs on MTurk.
To use them, you need to set the environment variables:

```bash
MTURK_AWS_ACCESS_KEY_ID=your_key
MTURK_AWS_SECRET_ACCESS_KEY=your_secret
```
