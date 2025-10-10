/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { ActionMenus } from "@web/search/action_menus/action_menus";

patch(ActionMenus.prototype, {
  async getActionItems(props) {
    var res = await super.getActionItems(props);
    if (this.props.resModel) {
      const isExportHidden = await this.orm.call(
        "access.right.mgmt",
        "is_export",
        [this.props.resModel],
        {}
      );
      const isArchive = await this.orm.call(
        "access.right.mgmt",
        "is_archive_unarchive",
        [this.props.resModel],
        {}
      );
      const actionsToRemove = [];
      if (isExportHidden) {
        actionsToRemove.push("export");
      }
      if (isArchive) {
        actionsToRemove.push("archive");
        actionsToRemove.push("unarchive");
      }
      if (actionsToRemove) {
        return res.filter((ele) => !actionsToRemove.includes(ele.key));
      }
    }

    return res;
  },
});
