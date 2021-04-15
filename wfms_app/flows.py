from viewflow import flow
from viewflow.base import this, Flow
from viewflow.flow.views import CreateProcessView, UpdateProcessView

from .models import HelloWorldProcess
from viewflow import frontend
from viewflow.lock import select_for_update_lock

from . import views
from .models import ShipmentProcess

@frontend.register
class HelloWorldFlow(Flow):
    process_class = HelloWorldProcess

    start = (
        flow.Start(
            CreateProcessView,
            fields=["text"]
        ).Permission(
            auto_create=True
        ).Next(this.approve)
    )

    approve = (
        flow.View(
            UpdateProcessView,
            fields=["approved"]
        ).Permission(
            auto_create=True
        ).Next(this.check_approve)
    )

    check_approve = (
        flow.If(lambda activation: activation.process.approved)
        .Then(this.send)
        .Else(this.end)
    )

    send = (
        flow.Handler(
            this.send_hello_world_request
        ).Next(this.end)
    )

    end = flow.End()

    def send_hello_world_request(self, activation):
        print(activation.process.text)

@frontend.register
class ShipmentFlow(Flow):
    """
    Shipment

    Shipment workflow for e-commerce store back-office automation
    """
    process_class = ShipmentProcess
    lock_impl = select_for_update_lock

    summary_template = """
        Shipment  items
        to   / 
        """

    start = (
        flow.Start(views.StartView)
        .Permission('shipment.can_start_request')
        .Next(this.split_clerk_warehouse)
    )

    # clerk
    split_clerk_warehouse = (
        flow.Split()
        .Next(this.shipment_type)
        .Next(this.package_goods)
    )

    shipment_type = (
        flow.View(
            views.ShipmentView, fields=["carrier"],
            task_description="Carrier selection")
        .Assign(lambda act: act.process.created_by)
        .Next(this.delivery_mode)
    )

    delivery_mode = (
        flow.If(cond=lambda act: act.process.is_normal_post())
        .Then(this.check_insurance)
        .Else(this.request_quotes)
    )

    request_quotes = (
        flow.View(
            views.ShipmentView,
            fields=["carrier_quote"])
        .Assign(lambda act: act.process.created_by)
        .Next(this.join_clerk_warehouse)
    )

    check_insurance = (
        flow.View(
            views.ShipmentView,
            fields=["need_insurance"])
        .Assign(lambda act: act.process.created_by)
        .Next('split_on_insurance')
    )

    split_on_insurance = (
        flow.Split()
        .Next(
            this.take_extra_insurance,
            cond=lambda act: act.process.need_extra_insurance())
        .Always(this.fill_post_label)
    )

    fill_post_label = (
        flow.View(
            views.ShipmentView,
            fields=["post_label"])
        .Assign(lambda act: act.process.created_by)
        .Next(this.join_on_insurance)
    )

    join_on_insurance = (
        flow.Join()
        .Next(this.join_clerk_warehouse)
    )

    # Logistic manager
    take_extra_insurance = (
        flow.View(views.InsuranceView)
        .Permission('shipment.can_take_extra_insurance')
        .Next(this.join_on_insurance)
    )

    # Warehouse worker
    package_goods = (
        flow.View(UpdateProcessView)
        .Permission('shipment.can_package_goods')
        .Next(this.join_clerk_warehouse)
    )

    join_clerk_warehouse = (
        flow.Join()
        .Next(this.move_package)
    )

    move_package = (
        flow.View(UpdateProcessView)
        .Assign(this.package_goods.owner)
        .Next(this.end)
    )

    end = flow.End()
