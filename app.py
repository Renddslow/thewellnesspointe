import json

from flask import Flask, g, render_template, jsonify, abort, request
from flaskext.markdown import Markdown
import requests
import sendgrid
from sendgrid.helpers.mail import *

application = Flask(__name__)
Markdown(application)
_file = open('./config.json', 'r')
config = json.loads(_file.read())
_file.close()
application.secret_key = config['secret_key']
sg = sendgrid.SendGridAPIClient(apikey=config['email_key'])
from_email = Email('customers@thewellnesspointe.com')
to_email = Email(config['to_email'])
config = None


@application.before_request
def before_request():
	_file = open('./config.json', 'r')
	g.config = json.loads(_file.read())
	_file.close()

@application.route('/')
def home():
	page_uri = '{}/entries/{}?access_token={}'.format(
		g.config['base_uri'],
		g.config['pages']['home'],
		g.config['api_key'])
	page = requests.get(page_uri).json()
	testimonial_uri = '{}/entries/{}?access_token={}'.format(
		g.config['base_uri'],
		page['fields']['testimonial']['sys']['id'],
		g.config['api_key'])
	testimonial = requests.get(testimonial_uri).json()
	blog_uri = '{}/entries?access_token={}&content_type={}'.format(
		g.config['base_uri'],
		g.config['api_key'],
		g.config['pages']['blog'])
	blog_posts = requests.get(blog_uri).json()
	return render_template('home.html',
							page=page['fields'],
							testimonial=testimonial['fields'],
							blog_posts=blog_posts['items'])


@application.route('/signup', methods=['POST'])
def signup():
	data = request.form
	if data['type'] == 'speaking':
		subject = '{} is interested in having Dr. Tapper speak'.format(data['name'])
		content = Content('text/plain', '{} has expressed interest in having Dr. Tapper speak at his or her organization as a part of his Wellness Made Simple series. Please follow up with him or her via their email: {}.\nThanks!'.format(
			data['name'],
			data['email']
		))
		mail = Mail(from_email, subject, to_email, content)
		response = sg.client.mail.send.post(request_body=mail.get())
		return jsonify({ 'message': 'You\'re all set!' })
	else:
		return jsonify({'message': 'Somethings wrong'}), 418


@application.route('/schedule/signup', methods=['POST'])
def schedule():
	data = request.form
	type_ = 'an adjustment' if data['type'] == '1' else 'a care plan'
	message = '<p>Hey team,</p><p><strong>{}</strong>'.format(data['name'])
	message = message + ' would like to set up {}.'.format(type_)
	message = message + '<p>Please reach out to them at <a href="mailto:{}">{}</a> '.format(
		data['email'],
		data['email']
	)
	message = message + 'or <a href="tel:{}">{}</a>.'.format(
		data['phone'],
		data['phone']
	)
	if data['subscribe']:
		message = message + '<p>{} would also like to be subscribed to our newsletter.</p>'.format(
			data['name']
		)
		message = message + '<p>Thanks so much!</p>'
	subject = '{} would like to set up an appointment'.format(data['name'])
	content = Content('text/html', message)
	mail = Mail(from_email, subject, to_email, content)
	response = sg.client.mail.send.post(request_body=mail.get())
	return jsonify({ 'message': 'You\'re all set!' })


@application.route('/blog')
def blog():
	return abort(404)


@application.route('/blog/<permalink>')
def blog_post(permalink):
	blog_post_uri = '{}/entries?access_token={}&&content_type=blogPost&fields.slug[match]={}'.format(
		g.config['base_uri'],
		g.config['api_key'],
		permalink
	)
	blog_post = requests.get(blog_post_uri).json()
	if blog_post['total'] > 0:
		blog_post = blog_post['items'][0]['fields']
		return render_template('post.html',
								page=blog_post,
								title=blog_post['title'])


@application.route('/<permalink>')
def pages(permalink):
	if permalink in g.config['pages']:
		title = permalink[0].upper() + permalink[1:]
		page_uri = '{}/entries/{}?access_token={}'.format(
			g.config['base_uri'],
			g.config['pages'][permalink],
			g.config['api_key'])
		page = requests.get(page_uri).json()
		if 'testimonial' in page['fields']:
			testimonial_uri = '{}/entries/{}?access_token={}'.format(
				g.config['base_uri'],
				page['fields']['testimonial']['sys']['id'],
				g.config['api_key'])
			testimonial = requests.get(testimonial_uri).json()['fields']
		else:
			testimonial = {}
		if 'callToAction' in page['fields']:
			action_uri = '{}/entries/{}?access_token={}'.format(
				g.config['base_uri'],
				page['fields']['callToAction']['sys']['id'],
				g.config['api_key'])
			action = requests.get(action_uri).json()['fields']
		else:
			action = {}
		type_ = request.args.get('type')
		return render_template('page.html',
								page=page['fields'],
								testimonial=testimonial,
								action=action,
								title=title,
								type=type_)
	else:
		return abort(404)





@application.errorhandler(404)
def page_not_found(e):
	return render_template("4xx.html",
							title="404 Page Not Found"), 404



if __name__ == "__main__":
	application.run(host='0.0.0.0')
