from django.db import models
from viewflow.models import Process, Task

# Create your models here.

class HelloWorldProcess(Process):
    text = models.CharField(max_length=150)
    approved = models.BooleanField(default=False)

class Carrier(models.Model):
    DEFAULT = 'Default'

    name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)

    def is_default(self):
        return self.name == Carrier.DEFAULT

    def __str__(self):
        return f'{self.name}'

class Insurance(models.Model):
    company_name = models.CharField(max_length=50)
    cost = models.IntegerField()

    def __str__(self):
        return '{} ${}'.format(self.company_name, self.cost)


class Shipment(models.Model):
    shipment_no = models.CharField(max_length=50)
    carrier = models.ForeignKey(Carrier, null=True, on_delete=models.CASCADE)

    # customer
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField()

    # shipment addres
    address = models.CharField(max_length=150)
    city = models.CharField(max_length=150)
    state = models.CharField(max_length=150)
    zipcode = models.CharField(max_length=10)
    country = models.CharField(max_length=150)
    phone = models.CharField(max_length=50)

    # shipment data
    need_insurance = models.BooleanField(default=False)
    insurance = models.ForeignKey('Insurance', null=True, on_delete=models.CASCADE)

    carrier_quote = models.IntegerField(default=0)
    post_label = models.TextField(blank=True, null=True)

    package_tag = models.CharField(max_length=50)


class ShipmentItem(models.Model):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE)
    name = models.CharField(max_length=250)
    quantity = models.IntegerField(default=1)


class ShipmentProcess(Process):
    shipment = models.ForeignKey(Shipment, blank=True, null=True, on_delete=models.CASCADE)

    def is_normal_post(self):
        try:
            if self.shipment.carrier:
                return self.shipment.carrier.is_default()
            else:
                return None
        except (Shipment.DoesNotExist, Carrier.DoesNotExist):
            return None

    def need_extra_insurance(self):
        try:
            return self.shipment.need_insurance
        except Shipment.DoesNotExist:
            return None

    class Meta:
        permissions = [  # Explicitly specified, but also can be autogenerated by Viewflow
            ('can_start_request', 'Can start shipment request'),
            ('can_take_extra_insurance', 'Can take extra insurance'),
            ('can_package_goods', 'Can package goods'),
            ('can_move_package', 'Can move package')
        ] 
