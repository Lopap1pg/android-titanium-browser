from pathlib import Path

# Titanium's fixed five-button bottom navigation:
#   Bookmarks | Forward | New Tab | Tab Switcher | Search
#
# The middle two actions stay on Chromium's native implementations. The three
# ordinary slots use small ActionRegistry models and call the browser's existing
# code paths rather than duplicating browser behaviour.


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Expected one match in {path}; found {count}: {old!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    print(f"Patched Titanium toolbar actions: {path}")


def replace_between(path: Path, start: str, end: str, replacement: str) -> None:
    text = path.read_text(encoding="utf-8")
    if replacement in text:
        return
    start_index = text.find(start)
    if start_index < 0:
        raise RuntimeError(f"Start marker not found in {path}: {start!r}")
    end_index = text.find(end, start_index)
    if end_index < 0:
        raise RuntimeError(f"End marker not found in {path}: {end!r}")
    path.write_text(text[:start_index] + replacement + text[end_index:], encoding="utf-8")
    print(f"Replaced Titanium toolbar section: {path}")


# ---------------------------------------------------------------------------
# Action IDs
# ---------------------------------------------------------------------------
action_id = Path(
    "chrome/browser/ui/android/actions/java/src/org/chromium/chrome/browser/ui/actions/ActionId.java"
)
replace_once(
    action_id,
    "    ActionId.AI_MODE,\n})",
    "    ActionId.AI_MODE,\n"
    "    ActionId.TITANIUM_PANEL,\n"
    "    ActionId.TITANIUM_FORWARD,\n"
    "    ActionId.TITANIUM_SEARCH,\n"
    "})",
)
replace_once(
    action_id,
    "    int AI_MODE = 6;\n}",
    "    int AI_MODE = 6;\n"
    "    int TITANIUM_PANEL = 7;\n"
    "    int TITANIUM_FORWARD = 8;\n"
    "    int TITANIUM_SEARCH = 9;\n"
    "}",
)

# ---------------------------------------------------------------------------
# Register visual models. Existing Chromium resources are intentionally reused.
# ---------------------------------------------------------------------------
action_utils = Path(
    "chrome/browser/ui/android/actions/java/src/org/chromium/chrome/browser/ui/actions/ActionUtils.java"
)
replace_once(
    action_utils,
    "        // Register new tab button.\n",
    "        // Register Titanium bookmarks/panel button.\n"
    "        registerAction(\n"
    "                registry,\n"
    "                ActionId.TITANIUM_PANEL,\n"
    "                ActionProperties.BASE_KEYS,\n"
    "                R.drawable.ic_star_24dp,\n"
    "                R.string.bookmarks,\n"
    "                R.string.bookmarks);\n\n"
    "        // Register Titanium forward button.\n"
    "        registerAction(\n"
    "                registry,\n"
    "                ActionId.TITANIUM_FORWARD,\n"
    "                ActionProperties.BASE_KEYS,\n"
    "                R.drawable.btn_forward,\n"
    "                R.string.accessibility_toolbar_btn_forward,\n"
    "                R.string.accessibility_toolbar_btn_forward);\n\n"
    "        // Register Titanium search button.\n"
    "        registerAction(\n"
    "                registry,\n"
    "                ActionId.TITANIUM_SEARCH,\n"
    "                ActionProperties.BASE_KEYS,\n"
    "                R.drawable.ic_search_24dp,\n"
    "                R.string.search,\n"
    "                R.string.search);\n\n"
    "        // Register new tab button.\n",
)

# ---------------------------------------------------------------------------
# Map the three custom actions into Bare-style physical slots.
# ---------------------------------------------------------------------------
layout = Path(
    "chrome/browser/ui/android/bottombar/java/src/org/chromium/chrome/browser/ui/bottombar/TitaniumToolbarLayout.java"
)
replace_once(
    layout,
    "        switch (actionId) {\n"
    "            case ActionId.HOME_BUTTON:\n"
    "                return TitaniumToolbarSlot.HOME;\n"
    "            case ActionId.GLIC:\n"
    "            case ActionId.AI_MODE:\n"
    "                return TitaniumToolbarSlot.EXTRA;\n",
    "        switch (actionId) {\n"
    "            case ActionId.TITANIUM_PANEL:\n"
    "            case ActionId.HOME_BUTTON:\n"
    "                return TitaniumToolbarSlot.HOME;\n"
    "            case ActionId.TITANIUM_FORWARD:\n"
    "            case ActionId.GLIC:\n"
    "            case ActionId.AI_MODE:\n"
    "                return TitaniumToolbarSlot.EXTRA;\n",
)
replace_once(
    layout,
    "            case ActionId.APP_MENU:\n"
    "                return TitaniumToolbarSlot.APP_MENU;\n",
    "            case ActionId.TITANIUM_SEARCH:\n"
    "            case ActionId.APP_MENU:\n"
    "                return TitaniumToolbarSlot.APP_MENU;\n",
)

# ---------------------------------------------------------------------------
# BottomBarCoordinator: five fixed actions, all five slots always populated.
# ---------------------------------------------------------------------------
coordinator = Path(
    "chrome/browser/ui/android/bottombar/java/src/org/chromium/chrome/browser/ui/bottombar/BottomBarCoordinator.java"
)
replace_once(
    coordinator,
    "        boolean shouldIncludeHomeButton = BottomBarConfigUtils.shouldIncludeHomeButtonIfEnabled();\n",
    "        // Titanium owns the first slot; do not let the homepage preference control it.\n"
    "        boolean shouldIncludeHomeButton = false;\n",
)

method_start = "    private List<ActionConfig> createActionConfigs(\n"
method_end = "    @Override\n    public View getView() {\n"
new_method = '''    private List<ActionConfig> createActionConfigs(
            BottomBarView view, boolean shouldIncludeHomeButton) {
        List<ActionConfig> configs = new ArrayList<>();

        BottomBarButtonContainer panelContainer =
                view.getContainerForAction(ActionId.TITANIUM_PANEL);
        assert panelContainer != null : "Titanium panel container not found";
        // Upstream's first slot normally contains Home, whose long-press view is special.
        // Titanium's panel action is an ordinary icon button.
        panelContainer.setStubLayoutResource(R.layout.bottom_bar_generic_template);
        configs.add(
                new ActionConfig(
                        ActionId.TITANIUM_PANEL,
                        panelContainer,
                        ActionButtonBinder::bind,
                        BottomBarProperties.IS_HOME_BUTTON_VISIBLE,
                        /* initiallyVisible= */ true));

        BottomBarButtonContainer forwardContainer =
                view.getContainerForAction(ActionId.TITANIUM_FORWARD);
        assert forwardContainer != null : "Titanium forward container not found";
        configs.add(
                new ActionConfig(
                        ActionId.TITANIUM_FORWARD,
                        forwardContainer,
                        ActionButtonBinder::bind,
                        BottomBarProperties.IS_EXTRA_BUTTON_VISIBLE,
                        /* initiallyVisible= */ true));

        BottomBarButtonContainer newTabContainer = view.getContainerForAction(ActionId.NEW_TAB);
        assert newTabContainer != null : "New tab container not found";
        configs.add(
                new ActionConfig(
                        ActionId.NEW_TAB,
                        newTabContainer,
                        ActionButtonBinder::bind,
                        BottomBarProperties.IS_NEW_TAB_BUTTON_VISIBLE,
                        /* initiallyVisible= */ true));

        BottomBarButtonContainer tabSwitcherContainer =
                view.getContainerForAction(ActionId.TAB_SWITCHER);
        assert tabSwitcherContainer != null : "Tab switcher container not found";
        configs.add(
                new ActionConfig(
                        ActionId.TAB_SWITCHER,
                        tabSwitcherContainer,
                        TabSwitcherActionButtonBinder::bind,
                        BottomBarProperties.IS_TAB_SWITCHER_BUTTON_VISIBLE,
                        /* initiallyVisible= */ true));

        BottomBarButtonContainer searchContainer =
                view.getContainerForAction(ActionId.TITANIUM_SEARCH);
        assert searchContainer != null : "Titanium search container not found";
        configs.add(
                new ActionConfig(
                        ActionId.TITANIUM_SEARCH,
                        searchContainer,
                        ActionButtonBinder::bind,
                        BottomBarProperties.IS_APP_MENU_BUTTON_VISIBLE,
                        /* initiallyVisible= */ true));

        return configs;
    }

'''
replace_between(coordinator, method_start, method_end, new_method)

# Chromium's startup bottom-bar promo is about its GLIC/AI surface and is not
# applicable to Titanium's fixed navigation bar.
promo_start = "    @Override\n    public boolean maybeShowPromoDialog(Profile profile) {\n"
promo_end = "    @Override\n    public void onStartupPromoFlowFinished(boolean promoShown) {\n"
new_promo = '''    @Override
    public boolean maybeShowPromoDialog(Profile profile) {
        return false;
    }

'''
replace_between(coordinator, promo_start, promo_end, new_promo)

# ---------------------------------------------------------------------------
# BottomBarMediator: the old shared GLIC/AI slot is now the permanent Forward
# slot. Keep its requested visibility on and bypass candidate/geofencing logic.
# ---------------------------------------------------------------------------
mediator = Path(
    "chrome/browser/ui/android/bottombar/java/src/org/chromium/chrome/browser/ui/bottombar/BottomBarMediator.java"
)
extra_start = "    private void updateExtraActionVisibility() {\n"
extra_end = "    private void updateGlicVisibility(@Nullable Profile originalProfile) {\n"
new_extra = '''    private void updateExtraActionVisibility() {
        if (mDestroyed) return;
        setButtonVisibility(ActionId.TITANIUM_FORWARD, /* visible= */ true);
    }

'''
replace_between(mediator, extra_start, extra_end, new_extra)

# ---------------------------------------------------------------------------
# Wire behaviour after the real LocationBar exists. This keeps all three
# actions on Chromium's existing implementations.
# ---------------------------------------------------------------------------
toolbar_manager = Path("chrome/android/java/src/org/chromium/chrome/browser/toolbar/ToolbarManager.java")
anchor = "        mLocationBar.addOmniboxSuggestionsDropdownScrollListener(mStatusBarColorController);\n\n"
block = '''        mLocationBar.addOmniboxSuggestionsDropdownScrollListener(mStatusBarColorController);

        if (mActionRegistry != null) {
            PropertyModel panelModel = mActionRegistry.get(ActionId.TITANIUM_PANEL).get();
            PropertyModel forwardModel = mActionRegistry.get(ActionId.TITANIUM_FORWARD).get();
            PropertyModel searchModel = mActionRegistry.get(ActionId.TITANIUM_SEARCH).get();
            assert panelModel != null : "TITANIUM_PANEL action should be registered";
            assert forwardModel != null : "TITANIUM_FORWARD action should be registered";
            assert searchModel != null : "TITANIUM_SEARCH action should be registered";

            panelModel.set(
                    ActionProperties.ON_PRESS_CALLBACK,
                    view -> {
                        Tab tab = mActivityTabProvider.get();
                        if (tab == null) return;
                        new org.chromium.chrome.browser.bookmarks.BookmarkManagerOpenerImpl()
                                .showBookmarkManager(mActivity, tab, tab.getProfile());
                    });

            forwardModel.set(
                    ActionProperties.ON_PRESS_CALLBACK,
                    view -> {
                        Tab tab = mActivityTabProvider.get();
                        if (tab != null && tab.canGoForward()) tab.goForward();
                    });

            searchModel.set(
                    ActionProperties.ON_PRESS_CALLBACK,
                    view ->
                            beginFuseboxInput(
                                    new AutocompleteInput(OmniboxFocusReason.OMNIBOX_TAP)));
        }

'''
replace_once(toolbar_manager, anchor, block)
