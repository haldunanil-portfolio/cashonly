This repo is for Cash Only website. _Guard it with your life._

If you have any questions, please email: [haldun@cashon.ly](mailto:haldun@cashon.ly)

# Introduction #

Currently, _Cash Only_ relies on the following frameworks and resources:

* AWS Elastic Beanstalk (EB), which includes:
    * AWS Elastic Compute Cloud (EC2)
    * AWS Relational Database Service (RDS)
    * AWS Simple Storage Service (S3)
    * AWS Elastic Load Balancer (ELB)
    * AWS Route 53
* PostgreSQL
* Django (Python 3.4)

# Using git & git Branching for Cash Only Feature Development #

This document is meant to outline how git is expected to be used for feature development at Cash Only. Please review this document regularly to ensure continued use of our most up-to-date git policy. A separate document for hotfixes can be found here.

_Updated: Monday, March 27, 2016._

## Overview ##

Please always ensure that you are using the most up-to-date stable version of git. As of the current date, the preferred version is git 2.10.1.

Cash Only uses Atlassian Bitbucket as our online repository. All new branches should first be created from the current version of the develop branch and pushed back so that they may all be merged properly later on. Please follow the steps outlined below every time you’re starting a new project.

The following draws heavily from [this article](http://nvie.com/posts/a-successful-git-branching-model/), and it is recommended that you read that before you continue, as this is essentially a summary steps article with the commentary removed.

## Step 1: Ensure that your local repo is up-to-date with the remote develop ##

Before starting any development, __you MUST ensure that your local repo is up-to-date with the remote server.__

If you do __NOT__ currently have a clone of the repo, please navigate to the folder you want to install in (one level above the root directory; e.g. Desktop if you want your root to be Desktop/cashonly) and type:

```shell
$ git clone -b develop https://bitbucket.org/cashonly/cashonly && cd cashonly
```

You may be prompted to enter username and password. Please enter to proceed. If you do not have one, contact [haldun@cashon.ly](mailto:haldun@cashon.ly) for assistance. If you do have a clone of the develop repo, update it via the following command (make sure you run this in the root directory):

```shell
$ git pull
```

## Step 2: Create a new local branch ##

Now, create your local branch via the following code (replace `myfeature` with an easy to remember name about the feature this branch is supposed to contain for development):

```shell
$ git checkout -b myfeature develop
```

Now that you’ve set up and are developing in the `myfeature` branch, please check on your editor (e.g. Atom, PyCharm, etc.) to make sure that you are indeed making edits to the right version.

## Step 3: Develop on your local branch ##

Develop as you normally would on your local branch. You are free to edit as many documents as you like, though ideally don’t go beyond editing the files that are necessary to implement your feature.

If you want to test your code, run the following in the terminal to run a server locally:

```shell
$ source activate ebenv
$ python manage.py runserver
```

If you get the following error, you’re not currently running a PostgreSQL server locally:

```
django.db.utils.OperationalError: could not connect to server: Connection refused
	Is the server running on host "localhost" (::1) and accepting
	TCP/IP connections on port 5432?
could not connect to server: Connection refused
	Is the server running on host "localhost" (127.0.0.1) and accepting
	TCP/IP connections on port 5432?
```

To fix, please go to Postgres.app and activate your server, then rerun the second line. Once you are done, make sure to add your changes to the git log by typing the following into terminal:

```shell
$ git add .
$ git commit -m "[EXPLAIN CHANGES IN 10 WORDS OR LESS]"
```

Make sure to explain what changes you’ve made in your branch clearly so that you (and others) can understand it in the future. Once you are done with your development, turn off your virtual environment via:

```shell
$ source deactivate
```

## Step 4: Merge to develop ##

In order to incorporate the new feature into the upcoming release, it must be merged back into develop. If, however, you need to collaborate with another developer on a particular feature (e.g. feature requires both backend and frontend work, development will take multiple sprints, etc.) then you may need to create a new secondary development branch. To do so, please contact admin.

To merge into develop, type the following into terminal (DON’T FORGET TO COMMIT YOUR CHANGES PER STEP 3):

```shell
$ git checkout develop
$ git merge --no-ff myfeature
$ git branch -d myfeature
```

Once you’ve followed the steps above, you will have merged your feature into your local clone of the develop branch and deleted the `myfeature` branch-- which means you’re ready to Bitbucket.

## Step 5: Push to Bitbucket repo ##

The last step is pushing your updates to the Bitbucket repo. Follow the steps below to do so:

```shell
$ git push origin develop
```

If you get any merge conflicts, please work with your counterparts to ensure that they are resolved before any production push.
