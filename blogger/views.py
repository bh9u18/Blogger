from django.shortcuts import render,redirect
from django.http import HttpResponseRedirect
from django.forms import inlineformset_factory
from django.urls import reverse,reverse_lazy
from django.views import generic
from .models import Blog, Category
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import User,auth
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm, BlogForm,UpdateBlogForm
from django.contrib import messages
from django.core import serializers
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from .filters import BlogFilter
from django.conf import settings
from django.core.mail import send_mail,EmailMessage
import django_filters
from braces import views
from django.utils import timezone
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.db.models import Q
# Create your views here.	
# def search(request):

	
# 	query=request.GET['query']

# 	if len(query)>78:
# 		allPosts = Blog.object.none()
# 	else:
# 		allPostsTitle = Blog.objects.filter(blog_name__icontains=query)
# 		allPostsContent = Blog.objects.filter(blog_text__icontains=query)
# 		allPosts = allPostsTitle.union(allPostsContent)

# 	if allPosts.count() != 0:
# 		params = {'allPosts': allPosts, 'query':query}
# 		page = render_to_string("include/results.html", params)
# 		return JsonResponse({'status': 'success', 'response': page})
# 	else:
# 		messages.warning(request, "No search result found. please refine your query")
# 		return JsonResponse({'status': 'fail'})
# def Ajaxsearch(request):
# 	ctx={}
# 	url_parameter=request.GET.get("q")
# 	if url_parameter:
# 		blogs=Blog.objects.filter(name__icontains=url_parameter)
# 	else:
# 		blogs=Blog.objects.all()
# 	ctx['blogs']=blogs
# 	if request.is_ajax():
# 		html=render_to_string(template_name="blogger/results.html",
# 		context={'blogs':blogs})
# 		data_dict={"html_from_view":html}
# 		return JsonResponse(data=data_dict,safe=False)

# 	return render(request,"blogger/search.html",context=ctx)


class IndexView(generic.ListView,views.JSONResponseMixin, views.AjaxResponseMixin):
	template_name='blogger/index.html'
	model=Blog
	order_by=['-date']
	paginate_by=5

	def get_queryset(self,**kwargs):
		queryset=BlogFilter(self.request.GET,queryset=Blog.objects.all().order_by('-date'))
		return queryset.qs

	def get_context_data(self,**kwargs):
		context=super().get_context_data(**kwargs)
		context['filter']=BlogFilter(self.request.GET,queryset=self.get_queryset())
		return context

	# def get(self,request,*args,**kwargs):
	# 	category=request.GET.get('category')
	# 	q=request.GET.get('q')
	# 	context=self.get_context_data()
	# 	print(context)
	# 	if request.is_ajax():
	# 		context=self.get_context_data()
	# 		return JsonResponse({'context':context},status=200)
	# 	return render(request,'blogger/index.html',context)


	# def get(self, request, *args, **kwargs):
	# 	ajax_list_partial = self.ajax_list_partial
	# 	self.object_list = super().get_queryset()
	# 	context = super().get_context_data(**kwargs)
	# 	if not ajax_list_partial:
	# 		raise TemplateDoesNotExist("No ajax__list_partial provided {}".format(self))
	# 		if request.is_ajax():
	# 			html_form = render_to_string(self.ajax__list_partial, context, request)
	# 			return JsonResponse({'html_form': html_form})
	# 		return super().get(request, *args, **kwargs)
	# def render_to_response(self):
	# 	return self.render_json_response(context)
	# def get_ajax(self,request):
	# 	import pdb;pdb.set_trace()
	# 	context_d=self.get_context_data()
	# 	return self.render_json_response(context_d)
def AjaxHandlerView(request):
	if request.method=='GET':
		# import pdb;pdb.set_trace()
		blog_list=Blog.objects.all().order_by("-date")
		
		blog_filter=BlogFilter(request.GET,queryset=blog_list)	
		if request.is_ajax():
			html=render_to_string(
				template_name="include/results.html",
				context={"filter":blog_filter})
			# blog_filter=BlogFilter(request.GET,queryset=blog_list)
			# data=serializers.serialize('json', blog_filter.qs)
			data_dict={'html_from_view':html}

			return JsonResponse(data=data_dict)
		else:
			blog_filter=BlogFilter(request.GET,queryset=blog_list)
		
	return render(request,'blogger/search.html',{'filter':blog_filter})

class DetailView(generic.DetailView):
	model=Blog
	template_name='blogger/details.html'

def registeration(request):
	form=CreateUserForm()

	if request.method == 'POST':
		form=CreateUserForm(request.POST)
		if form.is_valid():
			form.save()
			user=form.cleaned_data.get('username')
			messages.success(request,'Congratulations! Account is created for ' + user)
			return redirect('/login')

	context={'form':form}
	return render(request,'blogger/registeration.html',context)
	
def login(request):

	if request.method=='POST':
		username=request.POST.get('username')
		password=request.POST.get('password')
		
		user = authenticate(request,username=username, password=password)

		if user is not None:
			auth_login(request,user)
			return redirect('/')
		else:
			messages.info(request,"Username or password is incorrect")

	context = {}
	return render(request,'blogger/login.html',context)

def CategoryView(request,cats):

	category_blogs = Blog.objects.filter(category = cats)
	return render(request,'blogger/categories.html',{'cats':cats,'category_posts':category_blogs})

@login_required(login_url = '/login')
def logout(request):
	auth_logout(request)
	return redirect('/login')

@login_required(login_url = '/login')
def myblogs(request):
	blogs = Blog.objects.filter(author = request.user).order_by('-date')
	context = {'blogs':blogs}
	return render(request,'blogger/myblogs.html',context)
	
@method_decorator(login_required, name = 'dispatch')
class AddblogView(generic.CreateView):
	model = Blog
	form_class = BlogForm
	template_name = 'blogger/addblog.html'

	def post(self,request,*args,**kwargs):
		form = BlogForm(request.POST)
		if form.is_valid():
			
			blog = form.save(commit=False)
			blog.author = request.user
			blog.date = timezone.now()
			blog.save()
   
			# subject="Your post added successfully"
			# message=f'Hi {request.user}!!,Thankk you! Your post has been added successfully!'
			# email_from=settings.EMAIL_HOST_USER
			# recipent_list=[request.user.email]
			# send_mail(subject,message,email_from,recipent_list)
   		
			"""other_subject="New Post Update"
			other_message=f'Hey Everyone! New post has been added by {request.user}! GO and chcekout at our blogsite!! Thank you! Keep blogging.'
			other_email_from=settings.EMAIL_HOST_USER
			bcc=
			mail=EmailMessage(other_subject,other_message,other_email_from,[],bcc)
			mail.send()"""
   			#other_email.send()
			return HttpResponseRedirect('/')
		return render(request,self.template_name,{'form':form})

@method_decorator(login_required, name='dispatch')
class AddcategoryView(generic.CreateView):
	model = Category
	fields = '__all__'
	template_name = 'blogger/addcategory.html'

@method_decorator(login_required, name='dispatch')
class UpdateBlogView(generic.UpdateView):
	model = Blog
	form_class = UpdateBlogForm
	template_name = 'blogger/editblog.html'
	

@method_decorator(login_required, name = 'dispatch')
class DeleteBlogView(generic.DeleteView):
	model = Blog
	template_name = 'blogger/deleteblog.html'
	success_message = "Blog deleted"
	success_url = reverse_lazy('blogger:index')


"""
@method_decorator(login_required, name='dispatch')
class myblogsIndexView(generic.ListView):
	template_name='blogger/myblogs.html'
	context_object_name='users_latest_blog_list'
	paginate_by=5
	
	def get_username(request):
		username = Anonymous
		if request.user.is_authenticated():
			username= self.request.user
		return username
	
	def get_queryset(self):
		uname=get_username(request)
		return Blog.objects.filter(username=uname).order_by('-date')
"""
