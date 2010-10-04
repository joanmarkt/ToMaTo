package buildui.paint;
/*
 * Copyright (C) 2010 Dennis Schwerdel, University of Kaiserslautern
 * This file is part of ToMaTo (Topology management software)
 *
 * Emulab is free software, also known as "open source;" you can
 * redistribute it and/or modify it under the terms of the GNU Affero
 * General Public License as published by the Free Software Foundation,
 * either version 3 of the License, or (at your option) any later version.
 *
 * Emulab is distributed in the hope that it will be useful, but WITHOUT ANY
 * WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
 * FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for
 * more details, which can be found in the file AGPL-COPYING at the root of
 * the source tree.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

import buildui.Netbuild;
import java.awt.*;
import java.awt.event.*;
import java.util.Collection;
import java.util.regex.Pattern;

public class CheckboxField implements EditElement, ItemListener {

  public Checkbox checkbox;

  public CheckboxField(final PropertiesArea parent, String name, boolean def) {
    checkbox = new Checkbox(name, def);
    checkbox.addItemListener(this);
    checkbox.setForeground(Netbuild.glab_red);
    parent.addComponent(checkbox);
    checkbox.setVisible(true);
  }

  public void setValue (String t) {
    checkbox.setState(t.toLowerCase().equals("true")) ;
  }

  public String getValue () {
    return checkbox.getState() ? "true" : "false";
  }

  public void setEnabled (boolean enabled) {
    checkbox.setEnabled(enabled);
    if (enabled) checkbox.setBackground(Color.white);
    else checkbox.setBackground(Color.LIGHT_GRAY);
  }

  public boolean isEnabled () {
    return checkbox.isEnabled();
  }

  public void itemStateChanged (ItemEvent e) {
    //nothing to do
  }

}
    