import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";
import {localization} from "@web/core/l10n/localization";
import {formatFloat} from "@web/views/fields/formatters";
import {standardFieldProps} from "@web/views/fields/standard_field_props";
import {Component, useState, useEffect, onWillStart} from "@odoo/owl";
import {isMobileOS} from "@web/core/browser/feature_detection";

// Pop-up to show the information detailed by the warehouses
export class ProductWarehousePopOver extends Component {}
ProductWarehousePopOver.template = "stock_by_warehouse.ProductWarehousePopOver";

// Pop-up to show the information detailed by the locations
export class StockAvailabilityPopOver extends Component {}
StockAvailabilityPopOver.template = "stock_by_warehouse.StockAvailabilityPopOver";

// Main Widget
export class StockByWarehouseField extends Component {
    setup() {
        this.digits = 2;
        this.state = useState({
            info: {},
            show: formatFloat(0, {digits: this.digits}),
            lines: [],
        });
        this.popover = useService("popover");

        onWillStart(async () => {
            await this.formatData(this.props.record.data[this.props.name]);
        });
        useEffect(
            (val) => {
                this.formatData(val);
            },
            () => [this.props.record.data[this.props.name]]
        );
    }

    async formatData(rawData) {
        let info = {};
        if (typeof rawData === "string") {
            try {
                info = JSON.parse(rawData);
            } catch (e) {
                info = {};
                console.error("Error parsing warehouse info:", e);
            }
        } else {
            info = rawData || {};
        }

        if (!Object.keys(info).length) {
            Object.assign(this.state, {
                info: {},
                show: formatFloat(0, {digits: this.digits}),
                lines: [],
            });
            return;
        }

        this.state.info = info;
        this.state.show = formatFloat(this.props.byLocation ? info.available_locations || 0 : info.warehouse || 0, {
            digits: this.digits,
        });
        const lines = info.content || [];
        for (const value of lines) {
            value.available_not_res_formatted = formatFloat(value.available_not_res || 0, {digits: this.digits});
            value.available_formatted = formatFloat(value.available || 0, {digits: this.digits});
            value.incoming_formatted = formatFloat(value.incoming || 0, {digits: this.digits});
            value.outgoing_formatted = formatFloat(value.outgoing || 0, {digits: this.digits});
            value.virtual_formatted = formatFloat(value.virtual || 0, {digits: this.digits});
            value.saleable_formatted = formatFloat(value.saleable || 0, {digits: this.digits});
            value.locations_quantity_formatted = formatFloat(value.locations_available || 0, {digits: this.digits});
        }
        this.state.lines = lines;
    }

    onClick(ev) {
        const template = this.props.byLocation ? StockAvailabilityPopOver : ProductWarehousePopOver;
        this.popover.add(
            ev.currentTarget,
            template,
            {
                title: this.state.info.title,
                lines: this.state.lines,
            },
            {
                position: localization.direction === "rtl" || isMobileOS() ? "bottom" : "right",
            }
        );
    }
}

StockByWarehouseField.template = "stock_by_warehouse.ShowWarehouseInfo";
StockByWarehouseField.props = {
    ...standardFieldProps,
    byLocation: {type: Boolean, optional: true},
};

registry.category("fields").add("warehouse", {
    component: StockByWarehouseField,
    extractProps: ({options}) => ({
        byLocation: !!options.by_location,
    }),
});
