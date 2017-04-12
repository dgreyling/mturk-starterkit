# MTurk Starter Kit

This is a Flask app with Mechanical Turk integration, with the data stored on Firebase.
It comes with basic Heroku integration such that you can host it using the basic, free, 1-dyno machine.
The templating engine is based on Pug.


## Setup

### 1. Fork Repo

Fork the repo and clone it. Feel free to rename it to something more appropriate for your use case.

```bash
git clone https://github.com/vzhong/mturk-starterkit
```


### 2. Set up Heroku

```bash
heroku create <your app name>
```

Remember the name of the app, you will need when submitting jobs to MTurk.


### 3. Set up Firebase database

Create an account at [Firebase](https://firebase.google.com).
Make an app on Firebase - we will use the database functionality.
For simplicity, we actually will upload HIT data using the web interface, so your database don't need write access enabled.
However, all entries need to be readable (we won't bother securing read with authentication).
Hence, set the correct permission in to:

```json
{
  "rules": {
    ".read": true,
    ".write": false,
  }
}
```


### 4. Upload data to firebase

Your data upload will be a json file with the following format:

```json
{
  "examples": {
    "<example_id1>": {"id": "<example_id1>", "other": "fields"},
    "<example_id2>": {"id": "<example_id2>", "other": "fields"},
    "<example_id3>": {"id": "<example_id3>", "other": "fields"},
    "<example_id4>": {"id": "<example_id4>", "other": "fields"}
  }
}
```

Namely, there should be a top level entry of `examples`, under which is a dictionary of key value pairs in which each key is an example id and each value is the example json object.
Note that each example json object must also have an `id` field that is equal to its own example id.
After this, you should be able to go to Firebase's database and see that your data has been uploaded.


### 5. Make interface using Flask server

Now that the data has been uploaded, you can proceed to make your interface.
First, go to your Firebase app and go to "Add Firebase to your Web app" to find your app settings.
Fill this information into the file `firebase.config.json`.
The Flask server will use this information to retrieve data from your Firebase app.
Don't worry, it's ok if this information is publicly available - it's merely an identifier for your app.

You will most likely want to edit the following files:

- `example.pug`: how an individual HIT is rendered.
- `instructions.pug`: instructions for how to do a HIT.
- `examples.py`: examples of correct annotations, incorrect annotations, and reasons for why the latter are incorrect.


You may optionally want to edit `main.py`, which is the entrypoint to the Flask app, as well as `instruction_example.pug`, which specifies how each example in the instruction should be rendered.
Finally, `base.pug` contains the base template, which contains javascript and css imports.


In short, this is a normal Flask app, with one route active: `/example/<example_id>`.

To deploy your app to Heroku, simply do:

```bash
git push heroku
```

Note that while in development, your clicking the "Submit" button actually don't do anyting, as we will intercept the form submission because of the lack of an AssignmentId.

### 6. Submitting HITs to Mechanical Turk

We provide tools in the `mturk` folder to help you submit to and manage HITs on MTurk.
In order for this to work, you need to do the housekeeping.

First, you need to set up the following environment variables for authenticating with Mturk:

```bash
MTURK_AWS_ACCESS_KEY_ID=your_key
MTURK_AWS_SECRET_ACCESS_KEY=your_secret
```

Next, you need to set up the information workers will see when they visit the summary of your HIT on MTurk.
You can do this by modifying `turk.config.json`.

Finally, when you submit, you must give `submit.py` the name of your Firebase app, such that it can deduce the correct URL to direct workers to.

To manage your hits (e.g. accept, extend, count), use `manage.py`.
Similarly, you can reject hits using `reject.py`.

All binaries in the `mturk` folder come with `--help`, as well as `--prod`.
When you use the latter flag, you will communicate with the real production server instead of the sandbox server of Mturk.
