# =============================================================================
# Copyright (C) 2014 Alexandros Kosiaris
#
# This file is part of pyfa.
#
# pyfa is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyfa is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyfa.  If not, see <http://www.gnu.org/licenses/>.
# =============================================================================

# noinspection PyPackageRequirements
import wx
import gui.mainFrame
from gui.statsView import StatsView
from gui.bitmapLoader import BitmapLoader
from gui.utils.numberFormatter import formatAmount
from service.fit import Fit


class MiningYieldViewFull(StatsView):
    name = "miningyieldViewFull"

    def __init__(self, parent):
        StatsView.__init__(self)
        self.parent = parent
        self._cachedValues = []

    def getHeaderText(self, fit):
        return "Mining Yield"

    def getTextExtentW(self, text):
        width, height = self.parent.GetTextExtent(text)
        return width

    def populatePanel(self, contentPanel, headerPanel):
        contentSizer = contentPanel.GetSizer()
        parent = self.panel = contentPanel
        self.headerPanel = headerPanel

        panel = "full"

        sizerMiningYield = wx.FlexGridSizer(1, 4)
        sizerMiningYield.AddGrowableCol(1)

        contentSizer.Add(sizerMiningYield, 0, wx.EXPAND, 0)

        counter = 0

        for miningType, image in (("miner", "mining"), ("drone", "drones")):
            baseBox = wx.BoxSizer(wx.HORIZONTAL)
            sizerMiningYield.Add(baseBox, 1, wx.ALIGN_LEFT if counter == 0 else wx.ALIGN_CENTER_HORIZONTAL)

            baseBox.Add(BitmapLoader.getStaticBitmap("%s_big" % image, parent, "gui"), 0, wx.ALIGN_CENTER)

            box = wx.BoxSizer(wx.VERTICAL)
            baseBox.Add(box, 0, wx.ALIGN_CENTER)

            box.Add(wx.StaticText(parent, wx.ID_ANY, miningType.capitalize()), 0, wx.ALIGN_LEFT)

            hbox = wx.BoxSizer(wx.HORIZONTAL)
            box.Add(hbox, 1, wx.ALIGN_CENTER)

            lbl = wx.StaticText(parent, wx.ID_ANY, u"0.0 m\u00B3/s")
            setattr(self, "label%sminingyield%s" % (panel.capitalize(), miningType.capitalize()), lbl)

            hbox.Add(lbl, 0, wx.ALIGN_CENTER)
            self._cachedValues.append(0)
            counter += 1
        targetSizer = sizerMiningYield

        baseBox = wx.BoxSizer(wx.HORIZONTAL)
        targetSizer.Add(baseBox, 0, wx.ALIGN_LEFT)

        baseBox.Add(BitmapLoader.getStaticBitmap("cargoBay_big", parent, "gui"), 0, wx.ALIGN_CENTER)

        box = wx.BoxSizer(wx.VERTICAL)
        baseBox.Add(box, 0, wx.EXPAND)

        box.Add(wx.StaticText(parent, wx.ID_ANY, "Total"), 0, wx.ALIGN_LEFT)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(hbox, 1, wx.EXPAND)

        lbl = wx.StaticText(parent, wx.ID_ANY, u"0.0 m\u00B3/s")
        setattr(self, "label%sminingyieldTotal" % panel.capitalize(), lbl)
        hbox.Add(lbl, 0, wx.ALIGN_LEFT)

        self._cachedValues.append(0)

        image = BitmapLoader.getBitmap("turret_small", "gui")
        firepower = wx.BitmapButton(contentPanel, -1, image)
        firepower.SetToolTip(wx.ToolTip("Click to toggle to Firepower View"))
        firepower.Bind(wx.EVT_BUTTON, self.switchToFirepowerView)
        sizerMiningYield.Add(firepower, 0, wx.ALIGN_LEFT)

        self._cachedValues.append(0)

    def switchToFirepowerView(self, event):
        # Getting the active fit
        mainFrame = gui.mainFrame.MainFrame.getInstance()
        sFit = Fit.getInstance()
        fit = sFit.getFit(mainFrame.getActiveFit())
        # Remove ourselves from statsPane's view list
        self.parent.views.remove(self)
        self._cachedValues = []
        # And no longer display us
        self.panel.GetSizer().Clear(True)
        self.panel.GetSizer().Layout()
        # Get the new view
        view = StatsView.getView("firepowerViewFull")(self.parent)
        view.populatePanel(self.panel, self.headerPanel)
        # Populate us in statsPane's view list
        self.parent.views.append(view)
        # Get the TogglePanel
        tp = self.panel.GetParent()
        tp.SetLabel(view.getHeaderText(fit))
        view.refreshPanel(fit)

    def refreshPanel(self, fit):
        # If we did anything intresting, we'd update our labels to reflect the new fit's stats here

        stats = (("labelFullminingyieldMiner", lambda: fit.minerYield, 3, 0, 0, u"%s m\u00B3/s", None),
                 ("labelFullminingyieldDrone", lambda: fit.droneYield, 3, 0, 0, u"%s m\u00B3/s", None),
                 ("labelFullminingyieldTotal", lambda: fit.totalYield, 3, 0, 0, u"%s m\u00B3/s", None))

        counter = 0
        for labelName, value, prec, lowest, highest, valueFormat, altFormat in stats:
            label = getattr(self, labelName)
            value = value() if fit is not None else 0
            value = value if value is not None else 0
            if self._cachedValues[counter] != value:
                valueStr = formatAmount(value, prec, lowest, highest)
                label.SetLabel(valueFormat % valueStr)
                tipStr = "Mining Yield per second ({0} per hour)".format(formatAmount(value * 3600, 3, 0, 3))
                label.SetToolTip(wx.ToolTip(tipStr))
                self._cachedValues[counter] = value
            counter += 1
        self.panel.Layout()
        self.headerPanel.Layout()


MiningYieldViewFull.register()
