from django import forms


class OrderForm(forms.Form):
    
    PAYMENT_BY_CHOICES = (('M', 'in cash'),
                          ('C', 'by card'))
    
    name = forms.CharField(max_length=201)
    tel = forms.CharField(max_length=30)
    address = forms.CharField(max_length=300)
    comment = forms.CharField(widget=forms.Textarea, required=False,
        help_text='You can write down a comment about some additional details.')
    delivery_time = forms.CharField(max_length=50, required=False,
        help_text=('You can type either specific time or "As soon as possible",'
                   ' for example.'))
    payment_by = forms.ChoiceField(choices=PAYMENT_BY_CHOICES, initial='M')