/** @odoo-module **/

import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";
import {localization} from "@web/core/l10n/localization";
import {formatFloat} from "@web/views/fields/formatters";
import {textField, TextField} from "@web/views/fields/text/text_field";
import {archParseBoolean} from "@web/views/utils";
import {Component} from "@odoo/owl";
import {useSpecialData} from "@web/views/fields/relational_utils";

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
        this.popover = useService("popover");
        this.formatData(this.props);
        useSpecialData((orm, props) => {
            this.formatData(props);
            this.render();
        });
    }

    initializeVariables() {
        this.info = JSON.parse(this.props.record.data[this.props.name]);
        this.record_id = this.env.model.root.data.id;
        this.show = formatFloat(0, {digit: 2});
        this.lines = [];
    }

    formatData(props) {
        const info = JSON.parse(props.record.data[props.name]);
        if (this.record_id != this.env.model.root.data.id) {
            this.initializeVariables();
            return;
        }
        if (!Object.keys(info).length) {
            return;
        }
        this.info = info;
        this.show = formatFloat(this.props.byLocation ? this.info.available_locations : this.info.warehouse, {
            digit: 2,
        });
        this.lines = this.info.content || [];
        for (const value of this.lines) {
            value.available_not_res_formatted = formatFloat(value.available_not_res || 0, {digits: 2});
            value.available_formatted = formatFloat(value.available || 0, {digits: 2});
            value.incoming_formatted = formatFloat(value.incoming || 0, {digits: 2});
            value.outgoing_formatted = formatFloat(value.outgoing || 0, {digits: 2});
            value.virtual_formatted = formatFloat(value.virtual || 0, {digits: 2});
            value.saleable_formatted = formatFloat(value.saleable || 0, {digits: 2});
            value.locations_quantity_formatted = formatFloat(value.locations_available || 0, {digits: 2});
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

const textExtractProps = textField.extractProps;
export const stockByWarehouseField = {
    component: StockByWarehouseField,
    extractProps: (fieldInfo) => {
        return Object.assign(textExtractProps(fieldInfo), {
            byLocation: archParseBoolean(fieldInfo.options.by_location),
        });
    },
};

registry.category("fields").add("warehouse", stockByWarehouseField);
