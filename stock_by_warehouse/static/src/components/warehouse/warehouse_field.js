/** @odoo-module **/

import {registry} from "@web/core/registry";
import {usePopover} from "@web/core/popover/popover_hook";
import {localization} from "@web/core/l10n/localization";
import {formatFloat} from "@web/views/fields/formatters";
import {TextField} from "@web/views/fields/text/text_field";
import {archParseBoolean} from "@web/views/utils";

const {Component, onWillUpdateProps} = owl;

// Pop-up to show the information detailed by the warehouses
export class ProductWarehousePopOver extends Component {}
ProductWarehousePopOver.template = "stock_by_warehouse.ProductWarehousePopOver";

// Pop-up to show the information detailed by the locations
export class StockAvailabilityPopOver extends Component {}
StockAvailabilityPopOver.template = "stock_by_warehouse.StockAvailabilityPopOver";

// Main Widget
export class StockByWarehouseField extends TextField {
    setup() {
        this.initializeVariables();
        this.popover = usePopover();
        this.formatData(this.props);
        onWillUpdateProps((nextProps) => this.formatData(nextProps));
    }

    initializeVariables() {
        this.info = JSON.parse(this.props.value);
        this.record_id = this.env.model.root.data.id;
        this.show = formatFloat(0, {digit: 2});
        this.lines = [];
    }

    formatData(props) {
        const info = JSON.parse(props.value);
        if (this.record_id != this.env.model.root.data.id) {
            this.initializeVariables();
            return;
        }
        if (!info) {
            return;
        }
        this.info = info;
        this.show = formatFloat(this.props.byLocation ? this.info.available_locations : this.info.warehouse, {
            digit: 2,
        });
        this.lines = this.info.content || [];
        for (const value of this.lines) {
            value.available_not_res_formatted = formatFloat(value.available_not_res, {digits: 2});
            value.available_formatted = formatFloat(value.available, {digits: 2});
            value.incoming_formatted = formatFloat(value.incoming, {digits: 2});
            value.outgoing_formatted = formatFloat(value.outgoing, {digits: 2});
            value.virtual_formatted = formatFloat(value.virtual, {digits: 2});
            value.saleable_formatted = formatFloat(value.saleable, {digits: 2});
            value.locations_quantity_formatted = formatFloat(value.locations_available, {digits: 2});
        }
    }

    onClick(ev) {
        if (this.popoverCloseFn) {
            this.closePopover();
        }
        const template = this.props.byLocation ? StockAvailabilityPopOver : ProductWarehousePopOver;
        this.popoverCloseFn = this.popover.add(
            ev.currentTarget,
            template,
            {
                title: this.info.title,
                lines: this.lines,
                onClose: this.closePopover,
            },
            {
                position: localization.direction === "rtl" ? "bottom" : "right",
            }
        );
    }

    closePopover() {
        this.popoverCloseFn();
        this.popoverCloseFn = null;
    }
}
StockByWarehouseField.template = "stock_by_warehouse.ShowWarehouseInfo";

// Add the new option by_location to the props of the widget
StockByWarehouseField.props = {
    ...StockByWarehouseField.props,
    byLocation: {type: Boolean, optional: true},
};

const textExtractProps = StockByWarehouseField.extractProps;
StockByWarehouseField.extractProps = ({attrs, field}) => {
    return Object.assign(textExtractProps({attrs, field}), {
        byLocation: archParseBoolean(attrs.options.by_location),
    });
};

registry.category("fields").add("warehouse", StockByWarehouseField);
