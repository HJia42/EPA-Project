from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django import forms
from django.template import loader
from django.http import Http404

from US_zips import go, testing_US_df, is_true_zip
from map import *
from model_k import K_eco, get_k_eco_states


class ZipForm(forms.Form):
    #create zip_code field that is max 5 characters
    zip_code = forms.CharField(label='Zip Code', max_length=5, required=True)

    # check if input zip code is a true U.S. zip code
    def clean_zip_code(self):
        code = self.cleaned_data['zip_code']
        valid = is_true_zip(code)
        # raise error if not true zip code
        if not valid:
            raise forms.ValidationError("Please input a valid U.S. zip code!")
        return code


def homepg(request):
    context = {'tabs': {'About Our Model':'project:about', 
        'U.S. K-Map':'project:us_map', 'Meet the Team':'project:team'}}

    # if this is a POST request we need to process the form data,
    # indicates form was submitted
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ZipForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            input_zip = form.cleaned_data['zip_code']
            context['input_zip'] = input_zip

            # redirect to a new results page:
            try:
                K_model = K_eco(input_zip)
                state_df = K_model.k_df
                context['state'] = K_model.state
                context['city'] = K_model.city
                #print(context['city'])

                # Save plot as a svg data
                context['k_var'] = state_df.iloc[0]['K_var']
                #print(context['k_var'])
                context['map_svg'] = plot_kvars(state_df)
                #print('map done')
                
                '''
                ###comment out lines 43-53 and uncomment this section
                to see how front end should run with randomly 
                generated K-vars ################
                
                K_model = go(input_zip)
                data_zip = K_model[0]
                state_df = K_model[1]
                context['state'] = data_zip.iloc[0]['state_id']
                context['city'] = data_zip.iloc[0]['city']
                context['k_var'] = data_zip.iloc[0]['K_var']
                context['map_svg'] = plot_kvars(state_df)
                '''
            except Exception as e:
                print('Error caught: {}'.format(e))
            
            return render(request, 'results.html', context) 

    # if a GET (or any other method) we'll create a blank form
    else:
        form = ZipForm()

    context['form'] = form
    
    return render(request, 'base.html', context)


def results(request, zip_code):
    return render(request, 'results.html', context)


def about(request):
    context = {'tabs': {'About Our Model':'project:about',
                        'U.S. K-Map':'project:us_map', 'Meet the Team':'project:team'}}
    return render(request, 'about.html', context)


def team(request):
    context = {'tabs': {'About Our Model':'project:about',
                        'U.S. K-Map':'project:us_map', 'Meet the Team':'project:team'}}
    return render(request, 'team.html', context)


def us_map(request):
    context = {'tabs': {'About Our Model':'project:about',
                        'U.S. K-Map':'project:us_map', 'Meet the Team':'project:team'}}
    us_df = get_k_eco_states()
    '''
    If us_map page is taking too long to load, see what it looks like with randomly 
    generated US_k_df.
    
    Comment out line 101, uncomment code below

    us_df = testing_US_df()
    '''
    context['map_svg'] = find_us_map(us_df)
    return render(request, 'us_map.html', context)
