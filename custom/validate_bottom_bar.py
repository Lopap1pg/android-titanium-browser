from pathlib import Path

# Fail early, before GN/Ninja, if one of the source rewrites was skipped or an
# upstream patch left Titanium's bottom navigation only partially installed.
CHECKS = {
    Path("chrome/browser/flags/android/chrome_feature_list.cc"): [
        "BASE_FEATURE(kAndroidBottomBar, base::FEATURE_ENABLED_BY_DEFAULT);",
    ],
    Path(
        "chrome/browser/flags/android/java/src/org/chromium/chrome/browser/flags/ChromeFeatureList.java"
    ): [
        "newCachedFlag(ANDROID_BOTTOM_BAR, true, /* defaultValueInTests= */ true);",
        'newBooleanCachedFeatureParam(ANDROID_BOTTOM_BAR, "show_bottom_bar_on_gts", true);',
        'newBooleanCachedFeatureParam(ANDROID_BOTTOM_BAR, "disable_on_ntp", false);',
    ],
    Path(
        "chrome/browser/ui/android/actions/java/src/org/chromium/chrome/browser/ui/actions/ActionId.java"
    ): [
        "ActionId.TITANIUM_PANEL",
        "ActionId.TITANIUM_FORWARD",
        "ActionId.TITANIUM_SEARCH",
        "int TITANIUM_PANEL = 7;",
        "int TITANIUM_FORWARD = 8;",
        "int TITANIUM_SEARCH = 9;",
    ],
    Path(
        "chrome/browser/ui/android/actions/java/src/org/chromium/chrome/browser/ui/actions/ActionUtils.java"
    ): [
        "ActionId.TITANIUM_PANEL",
        "R.drawable.ic_star_24dp",
        "ActionId.TITANIUM_FORWARD",
        "R.drawable.btn_forward",
        "ActionId.TITANIUM_SEARCH",
        "R.drawable.ic_search_24dp",
    ],
    Path(
        "chrome/browser/ui/android/bottombar/java/res/layout/bottom_bar_layout.xml"
    ): [
        'android:id="@+id/new_tab_button_container"',
        'android:id="@+id/tab_switcher_button_container"',
    ],
    Path(
        "chrome/browser/ui/android/bottombar/java/src/org/chromium/chrome/browser/ui/bottombar/TitaniumToolbarSlot.java"
    ): [
        "int COUNT = 5;",
        "int NEW_TAB = 2;",
        "int TAB_SWITCHER = 3;",
    ],
    Path(
        "chrome/browser/ui/android/bottombar/java/src/org/chromium/chrome/browser/ui/bottombar/TitaniumToolbarLayout.java"
    ): [
        "case ActionId.TITANIUM_PANEL:",
        "case ActionId.TITANIUM_FORWARD:",
        "case ActionId.TITANIUM_SEARCH:",
    ],
    Path(
        "chrome/browser/ui/android/bottombar/java/src/org/chromium/chrome/browser/ui/bottombar/BottomBarView.java"
    ): [
        "mSlotContainers = new BottomBarButtonContainer[TitaniumToolbarSlot.COUNT];",
        "TitaniumToolbarLayout.slotForAction(actionId)",
    ],
    Path(
        "chrome/browser/ui/android/bottombar/java/src/org/chromium/chrome/browser/ui/bottombar/BottomBarCoordinator.java"
    ): [
        "ActionId.TITANIUM_PANEL",
        "ActionId.TITANIUM_FORWARD",
        "ActionId.NEW_TAB",
        "ActionId.TAB_SWITCHER",
        "ActionId.TITANIUM_SEARCH",
        "public boolean maybeShowPromoDialog(Profile profile) {\n        return false;",
    ],
    Path(
        "chrome/browser/ui/android/bottombar/java/src/org/chromium/chrome/browser/ui/bottombar/BottomBarMediator.java"
    ): [
        "setButtonVisibility(ActionId.TITANIUM_FORWARD, /* visible= */ true);",
    ],
    Path("chrome/android/java/src/org/chromium/chrome/browser/toolbar/ToolbarManager.java"): [
        "BookmarkManagerOpenerImpl",
        "ActionId.TITANIUM_SEARCH",
        "beginFuseboxInput(",
        "private void updateTitaniumForwardAction()",
        "mToolbarTabController.forward()",
    ],
}

failures = []
for path, needles in CHECKS.items():
    if not path.exists():
        failures.append(f"missing file: {path}")
        continue

    text = path.read_text(encoding="utf-8")
    for needle in needles:
        if needle not in text:
            failures.append(f"{path}: missing {needle!r}")

if failures:
    raise RuntimeError(
        "Titanium bottom-bar validation failed:\n  - " + "\n  - ".join(failures)
    )

print("Titanium bottom-bar source validation passed.")
