from pathlib import Path

# Structural port of Bare Browser patch 0100 for Titanium.
# This intentionally ports only the five-slot abstraction. Bare-specific
# preferences and the Bare incognito action are not imported.

PACKAGE_DIR = Path(
    "chrome/browser/ui/android/bottombar/java/src/org/chromium/chrome/browser/ui/bottombar"
)

SLOT_SOURCE = r'''// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package org.chromium.chrome.browser.ui.bottombar;

import androidx.annotation.IntDef;

import org.chromium.build.annotations.NullMarked;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/** Identifies one of Titanium's five bottom-bar positions, from left to right. */
@IntDef({
    TitaniumToolbarSlot.HOME,
    TitaniumToolbarSlot.EXTRA,
    TitaniumToolbarSlot.NEW_TAB,
    TitaniumToolbarSlot.TAB_SWITCHER,
    TitaniumToolbarSlot.APP_MENU,
})
@Retention(RetentionPolicy.SOURCE)
@Target(ElementType.TYPE_USE)
@NullMarked
public @interface TitaniumToolbarSlot {
    int HOME = 0;
    int EXTRA = 1;
    int NEW_TAB = 2;
    int TAB_SWITCHER = 3;
    int APP_MENU = 4;

    int COUNT = 5;
    int NONE = -1;
}
'''

LAYOUT_SOURCE = r'''// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package org.chromium.chrome.browser.ui.bottombar;

import org.chromium.build.annotations.NullMarked;
import org.chromium.chrome.browser.ui.actions.ActionId;

/** Maps browser actions to physical positions in Titanium's five-slot bottom bar. */
@NullMarked
public final class TitaniumToolbarLayout {
    private TitaniumToolbarLayout() {}

    public static @TitaniumToolbarSlot int slotForAction(@ActionId int actionId) {
        switch (actionId) {
            case ActionId.HOME_BUTTON:
                return TitaniumToolbarSlot.HOME;
            case ActionId.GLIC:
            case ActionId.AI_MODE:
                return TitaniumToolbarSlot.EXTRA;
            case ActionId.NEW_TAB:
                return TitaniumToolbarSlot.NEW_TAB;
            case ActionId.TAB_SWITCHER:
                return TitaniumToolbarSlot.TAB_SWITCHER;
            case ActionId.APP_MENU:
                return TitaniumToolbarSlot.APP_MENU;
            default:
                return TitaniumToolbarSlot.NONE;
        }
    }
}
'''


def write_generated(path: Path, content: str) -> None:
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"Wrote Titanium bottom-bar source: {path}")


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Expected one match in {path}; found {count}: {old!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    print(f"Patched Titanium five-slot bottom bar: {path}")


write_generated(PACKAGE_DIR / "TitaniumToolbarSlot.java", SLOT_SOURCE)
write_generated(PACKAGE_DIR / "TitaniumToolbarLayout.java", LAYOUT_SOURCE)

build_gn = Path("chrome/browser/ui/android/bottombar/BUILD.gn")
replace_once(
    build_gn,
    '    "java/src/org/chromium/chrome/browser/ui/bottombar/AppMenuActionButtonBinder.java",\n',
    '    "java/src/org/chromium/chrome/browser/ui/bottombar/AppMenuActionButtonBinder.java",\n'
    '    "java/src/org/chromium/chrome/browser/ui/bottombar/TitaniumToolbarLayout.java",\n'
    '    "java/src/org/chromium/chrome/browser/ui/bottombar/TitaniumToolbarSlot.java",\n',
)

layout = Path("chrome/browser/ui/android/bottombar/java/res/layout/bottom_bar_layout.xml")
replace_once(
    layout,
    "    <org.chromium.chrome.browser.ui.bottombar.BottomBarButtonContainer\n"
    "        android:layout_width=\"0dp\"\n"
    "        android:layout_height=\"match_parent\"\n"
    "        android:layout_weight=\"1\">\n"
    "        <!-- Padding is used to define the bounds of the IPH highlight\n",
    "    <org.chromium.chrome.browser.ui.bottombar.BottomBarButtonContainer\n"
    "        android:id=\"@+id/new_tab_button_container\"\n"
    "        android:layout_width=\"0dp\"\n"
    "        android:layout_height=\"match_parent\"\n"
    "        android:layout_weight=\"1\">\n"
    "        <!-- Padding is used to define the bounds of the IPH highlight\n",
)
replace_once(
    layout,
    "    <org.chromium.chrome.browser.ui.bottombar.BottomBarButtonContainer\n"
    "        android:layout_width=\"0dp\"\n"
    "        android:layout_height=\"match_parent\"\n"
    "        android:layout_weight=\"1\">\n"
    "        <org.chromium.chrome.browser.ui.android.bars_common.TabSwitcherButtonView\n",
    "    <org.chromium.chrome.browser.ui.bottombar.BottomBarButtonContainer\n"
    "        android:id=\"@+id/tab_switcher_button_container\"\n"
    "        android:layout_width=\"0dp\"\n"
    "        android:layout_height=\"match_parent\"\n"
    "        android:layout_weight=\"1\">\n"
    "        <org.chromium.chrome.browser.ui.android.bars_common.TabSwitcherButtonView\n",
)

view = PACKAGE_DIR / "BottomBarView.java"
replace_once(
    view,
    "    private BottomBarButtonContainer[] mOtherContainers;\n"
    "    private RippleDrawable[] mOtherRipples;\n",
    "    private BottomBarButtonContainer[] mOtherContainers;\n"
    "    private BottomBarButtonContainer[] mSlotContainers;\n"
    "    private RippleDrawable[] mOtherRipples;\n",
)
replace_once(
    view,
    "        mNewTabButton = findViewById(R.id.new_tab_button);\n"
    "        mNewTabContainer = (BottomBarButtonContainer) mNewTabButton.getParent();\n\n"
    "        View tabSwitcherButton = findViewById(R.id.tab_switcher_button);\n"
    "        mTabSwitcherContainer = (BottomBarButtonContainer) tabSwitcherButton.getParent();\n\n"
    "        mAppMenuContainer = findViewById(R.id.app_menu_button_container);\n",
    "        mNewTabButton = findViewById(R.id.new_tab_button);\n"
    "        mNewTabContainer = findViewById(R.id.new_tab_button_container);\n\n"
    "        mTabSwitcherContainer = findViewById(R.id.tab_switcher_button_container);\n\n"
    "        mAppMenuContainer = findViewById(R.id.app_menu_button_container);\n\n"
    "        mSlotContainers = new BottomBarButtonContainer[TitaniumToolbarSlot.COUNT];\n"
    "        mSlotContainers[TitaniumToolbarSlot.HOME] = mHomeContainer;\n"
    "        mSlotContainers[TitaniumToolbarSlot.EXTRA] = mExtraContainer;\n"
    "        mSlotContainers[TitaniumToolbarSlot.NEW_TAB] = mNewTabContainer;\n"
    "        mSlotContainers[TitaniumToolbarSlot.TAB_SWITCHER] = mTabSwitcherContainer;\n"
    "        mSlotContainers[TitaniumToolbarSlot.APP_MENU] = mAppMenuContainer;\n",
)
replace_once(
    view,
    "    @Nullable BottomBarButtonContainer getContainerForAction(@ActionId int actionId) {\n"
    "        switch (actionId) {\n"
    "            case ActionId.HOME_BUTTON:\n"
    "                return mHomeContainer;\n"
    "            case ActionId.GLIC:\n"
    "            case ActionId.AI_MODE:\n"
    "                return mExtraContainer;\n"
    "            case ActionId.NEW_TAB:\n"
    "                return mNewTabContainer;\n"
    "            case ActionId.TAB_SWITCHER:\n"
    "                return mTabSwitcherContainer;\n"
    "            case ActionId.APP_MENU:\n"
    "                return mAppMenuContainer;\n"
    "            default:\n"
    "                return null;\n"
    "        }\n"
    "    }\n",
    "    @Nullable BottomBarButtonContainer getContainerForAction(@ActionId int actionId) {\n"
    "        @TitaniumToolbarSlot int slot = TitaniumToolbarLayout.slotForAction(actionId);\n"
    "        if (slot == TitaniumToolbarSlot.NONE) return null;\n"
    "        return mSlotContainers[slot];\n"
    "    }\n",
)
