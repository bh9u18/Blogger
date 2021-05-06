import django_filters
from .models import *
from django import forms
from django.db.models import Q

class BlogFilter(django_filters.FilterSet):
	
	q=django_filters.CharFilter(method='my_custom_filter',label='Search')
	def my_custom_filter(self,queryset,name,value):
		return queryset.filter( Q(blog_name__icontains=value) | Q(blog_text__icontains=value)).order_by('-date') 

	class Meta:
		model=Blog
		fields=['category','q']

	
        