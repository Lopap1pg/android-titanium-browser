from pathlib import Path

# Titanium adaptation of Bare Browser's Chromium Android bottom-bar enablement.
# Reference patches in Lopap1pg/bare-browser:
#   0028-Move-the-tab-switcher-toolbar-to-the-bottom.patch
#   0120-Keep-the-bottom-bar-on-the-new-tab-page.patch
#
# Keep this as narrow source rewriting instead of importing Bare's whole patch
# series. Titanium applies Vanadium/Titanium changes first; these replacements
# run afterwards against the resulting Chromium tree.

REPLACEMENTS = {
    Path("chrome/browser/flags/android/chrome_feature_list.cc"): [
        (
            "BASE_FEATURE(kAndroidBottomBar, base::FEATURE_DISABLED_BY_DEFAULT);",
            "BASE_FEATURE(kAndroidBottomBar, base::FEATURE_ENABLED_BY_DEFAULT);",
        ),
    ],
    Path(
        "chrome/browser/flags/android/java/src/org/chromium/chrome/browser/flags/ChromeFeatureList.java"
    ): [
        (
            "newCachedFlag(ANDROID_BOTTOM_BAR, false, /* defaultValueInTests= */ true);",
            "newCachedFlag(ANDROID_BOTTOM_BAR, true, /* defaultValueInTests= */ true);",
        ),
        (
            'newBooleanCachedFeatureParam(ANDROID_BOTTOM_BAR, "show_bottom_bar_on_gts", false);',
            'newBooleanCachedFeatureParam(ANDROID_BOTTOM_BAR, "show_bottom_bar_on_gts", true);',
        ),
        (
            'newBooleanCachedFeatureParam(ANDROID_BOTTOM_BAR, "disable_on_ntp", true);',
            'newBooleanCachedFeatureParam(ANDROID_BOTTOM_BAR, "disable_on_ntp", false);',
        ),
    ],
}


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")

    if new in text:
        # Idempotent when the build script is re-run in an already patched tree.
        return

    count = text.count(old)
    if count != 1:
        raise RuntimeError(
            f"Expected exactly one match in {path}: {old!r}; found {count}"
        )

    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    print(f"Enabled Chromium bottom-bar setting in {path}: {old} -> {new}")


for target, replacements in REPLACEMENTS.items():
    if not target.exists():
        raise RuntimeError(f"Chromium bottom-bar target not found: {target}")

    for old, new in replacements:
        replace_once(target, old, new)
