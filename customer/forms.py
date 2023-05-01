
from django import forms

class CustomerCheckoutForm(forms.Form):
    phone = forms.CharField(widget = forms.TextInput(attrs={'class':'form-control','placeholder':'Mobile number'}),max_length= 200, required=True)
    address = forms.CharField(widget = forms.Textarea(attrs={'class':'form-control','placeholder':'Delivery address',"rows":5}),max_length= 2000, required=True)