# Access Academy
[Access Academy](https://access-academy.herokuapp.com/)

## What is Access Academy?

Access Academy is a place where users can design courses for others or design their own learning path.  Users might be looking to gain a new skill or study for a professional certification exam. A customized learning path allows a user to curate material that is most relevant for them and leave out material they are already comfortable with.

## Get Started Using Access Academy

### Try it out.
To explore the features of this site without creating an account, navigate to the homepage and click on the "demo account" link to access a pre-made demo account.
### Sign up for an account.
A user starts by creating an account on the site. There are links to "Sign up" on the home page. The user's password is stored securely in the database in a hashed format. 

Successful creation of an account logs the user in.  

## Returning Users

### Log in

Returning users who are not already logged in should click "Log in" from the navigation bar. 

Once logged in, a user is able to:
* view existing courses and watch the videos within them
* search for a course using a keyword or phrase
* create new courses
* view a page showing the courses they have created
* add, delete, or resequence the videos in a course they've created

### View existing courses
Click "Search" in the navigation bar at the top of the page. Some existing courses will be shown initially by default. 
To see all courses, click the Search button without a search term.

### Search for a course
On the same page, enter a search term, and the app will search course titles for that term.
### Create a course

Click the "Create course" link in the navigation bar to be taken to a page where a course title (required) and description (optional) can be entered.

### Video search page

After creating a new course, the user is brought to the videos search page. From here, execute a keyword search of YouTube videos. A list of video "cards" will appear on the page. Click on the "Add to course" button to add a video to the end of the course. 

The order of videos can be changed later on the 'Modify course' page.

Also on the video search page is a link to view the list of videos in the course. 
### View your courses

Logged in users can see the courses they've created at any time by clicking "My Courses" from the navigation bar.

### View the list of videos in a course

From the list of courses shown on any page, such as the courses search page, click on a video thumbnail image to be taken to YouTube to watch it.

When viewing the videos in a course, there are two links _visible only to the course creator_ :
* Search for videos - this takes the user back to the videos search page
* Modify the course - this takes the user to a page where the course videos can be resequenced or removed.

### Modify a course

On this page, which is visible only to the course creator, there is a list of video cards, one for each video in the course.  When viewing this page for the first time, the videos are listed in the order they were added to the course.

All videos will show a red "Remove" button that, when clicked, will remove the video from the course. If there is only one video in the course, the "Remove" button will be the only button shown.

There will be as many as three buttons on each video card, including the "Remove" button. The other two buttons are for resequencing the videos within the course. The up arrow button moves the video up one position, and the video that was previously in that position moves down to take its place. The down arrow button similarly causes the video to switch places with the video below it.

## Site features

### Account security

User passwords are hashed and stored securely. 
### Course search

The courses titles can be searched by word or phrase within the title. This is better than a full title search, because sometimes people remember only part of the title. The search is case-insensitive for better results.
### Course modification

The pages that can be used to modify the course (i.e., videos search page and modify course page) are visible only to the course creators. No one wants the course they worked hard to create to be modified by someone else.

### Video links 

The videos for each course do not currently play on the site. Instead, clicking a video thumbnail takes the user to the source of the video on YouTube. This was a necessary choice for now, because there is too much of a delay in loading embedded videos on a page.

Ideally, the videos would be embedded on the site and playable from there without delay. This is one of many goals for a future version of this app.
### Site design
The site uses a simple, clean design intentionally to keep the focus on the content.

The color blue was chosen because it is associated with reliability and symbolizes wisdom. Access Academy wants to be seen as a trusted site for gaining knowledge and skills, so this was a great color choice in that regard. Blue is also known to have a calming effect on people, which is helpful when a person is trying to learn new things.

## Inspiration for this site

I am passionate about empowering people to help themselves in their education and professional careers. It is important that everyone have an equal opportunity to access quality education and test preparation resources, regardless of their socioeconomic status.  My hope is that this site will make it easier for people to create the resources for themselves that may already exist as a service but be out of reach financially for some.

## Tech Stack

This is a full-stack app that runs Python on the backend with the Flask framework. The front end uses HTML, CSS, Bootstrap, and JavaScript.

The database is built with a PostgreSQL database engine, and the Flask-SQLAlchemy ORM is used to create and query the database. 

WTForms is used to create many of the forms.
## External API
I used the search method of Google's YouTube Data API: [YouTube Data API](https://developers.google.com/youtube/v3/search) to search for videos by keyword phrase.

The search returns information about each video, including a thumbnail image.  To return an embedded iframe element, use this search in conjunction with the videos method. 

See the [YouTube Data API](https://developers.google.com/youtube/v3/search) for details on the videos method.

## Set up app - for developers

* Download the repo from GitHub.

* Create a Python virtual environment and activate it locally. Many of the following steps require you to be in the virtual environment.

* Install dependencies:
  ```
  pip install -r requirements.txt
  ```
  Note that this project uses Python 3.85, which I have installed globally. You will need either a global installation or venv installation of Python 3.85 in addition to the dependencies listed in requirements.txt.

* Get an API key from Google's YouTube Data API and put it in a file called 'secrets.py' using one line of the following form:
API_SECRET_KEY = "<<insert_key_string_here>>"

* Install PostgreSQL locally and make sure that it is running on port 5432.

* Create a PostgreSQL database called 'access-academy'.

* Run the seed file to populate the database with users and (empty) courses:
  ```
  python3 seed.py 
  ```