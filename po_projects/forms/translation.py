# -*- coding: utf-8 -*-
"""
Forms for po_projects translation messages
"""
from django.conf import settings
from django import forms
from django.utils.translation import ugettext_lazy as _

from po_projects.models import TranslationMsg
from po_projects.forms.crispies import translation_helper

class TranslationMsgForm(forms.ModelForm):
    """Translation Form"""
    def __init__(self, *args, **kwargs):

        super(TranslationMsgForm, self).__init__(*args, **kwargs)
        
        if self.instance.fuzzy:
            self.fields['fuzzy'].label = _("Fuzzy")
        else:
            self.fields['fuzzy'].label = _("Enabled")
        
        self.helper = translation_helper(self.instance, self.prefix)

    def save(self, commit=True):
        message = super(TranslationMsgForm, self).save(commit=False)
        
        if commit:
            message.save()
            
        return message

    class Meta:
        model = TranslationMsg
        exclude = ('catalog',)
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3}),
        }

