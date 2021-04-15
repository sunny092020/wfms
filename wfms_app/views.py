from django.shortcuts import render
from django.views import generic
from viewflow.flow.views import StartFlowMixin, FlowViewMixin

from .forms import ShipmentForm
from .models import Insurance

# Create your views here.
class StartView(StartFlowMixin, generic.UpdateView):
    form_class = ShipmentForm

    def get_object(self):
        return self.activation.process.shipment

    def activation_done(self, form):
        shipment = form.save()
        self.activation.process.shipment = shipment
        super(StartView, self).activation_done(form)


class ShipmentView(FlowViewMixin, generic.UpdateView):
    def get_object(self):
        return self.activation.process.shipment


class InsuranceView(FlowViewMixin, generic.CreateView):
    model = Insurance
    fields = ['company_name', 'cost']

    def activation_done(self, form):
        shipment = self.activation.process.shipment
        shipment.insurance = self.object
        shipment.save(update_fields=['insurance'])
        self.activation.done()
