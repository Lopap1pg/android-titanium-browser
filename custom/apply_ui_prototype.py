from pathlib import Path

TARGETS = [
    Path("chrome/android/java/res_app/layout/main.xml"),
    Path("chrome/android/java/res_app/layout/main_forked_with_secondary_ui_container.xml"),
]

MARKER = "<!-- TITANIUM_CUSTOM_NAV_PROTOTYPE -->"
ANCHOR = "    </org.chromium.components.browser_ui.widget.CoordinatorLayoutForPointer>"

BLOCK = r'''        <!-- TITANIUM_CUSTOM_NAV_PROTOTYPE -->
        <LinearLayout
            android:id="@+id/titanium_custom_nav_prototype"
            android:layout_width="match_parent"
            android:layout_height="56dp"
            android:layout_gravity="bottom"
            android:layout_marginBottom="24dp"
            android:background="@macro/toolbar_background_primary"
            android:elevation="8dp"
            android:orientation="horizontal"
            android:paddingStart="4dp"
            android:paddingEnd="4dp">

            <TextView
                android:id="@+id/titanium_proto_panel"
                android:layout_width="0dp"
                android:layout_height="match_parent"
                android:layout_weight="1"
                android:background="?attr/selectableItemBackgroundBorderless"
                android:clickable="true"
                android:focusable="true"
                android:gravity="center"
                android:text="▤"
                android:textColor="?android:attr/textColorPrimary"
                android:textSize="25sp" />

            <TextView
                android:id="@+id/titanium_proto_forward"
                android:layout_width="0dp"
                android:layout_height="match_parent"
                android:layout_weight="1"
                android:background="?attr/selectableItemBackgroundBorderless"
                android:clickable="true"
                android:focusable="true"
                android:gravity="center"
                android:text="→"
                android:textColor="?android:attr/textColorPrimary"
                android:textSize="27sp" />

            <TextView
                android:id="@+id/titanium_proto_new_tab"
                android:layout_width="0dp"
                android:layout_height="match_parent"
                android:layout_weight="1"
                android:background="?attr/selectableItemBackgroundBorderless"
                android:clickable="true"
                android:focusable="true"
                android:gravity="center"
                android:text="＋"
                android:textColor="?android:attr/textColorPrimary"
                android:textSize="28sp" />

            <TextView
                android:id="@+id/titanium_proto_tabs"
                android:layout_width="0dp"
                android:layout_height="match_parent"
                android:layout_weight="1"
                android:background="?attr/selectableItemBackgroundBorderless"
                android:clickable="true"
                android:focusable="true"
                android:gravity="center"
                android:text="▣"
                android:textColor="?android:attr/textColorPrimary"
                android:textSize="24sp" />

            <TextView
                android:id="@+id/titanium_proto_search"
                android:layout_width="0dp"
                android:layout_height="match_parent"
                android:layout_weight="1"
                android:background="?attr/selectableItemBackgroundBorderless"
                android:clickable="true"
                android:focusable="true"
                android:gravity="center"
                android:text="⌕"
                android:textColor="?android:attr/textColorPrimary"
                android:textSize="28sp" />
        </LinearLayout>
'''

for target in TARGETS:
    text = target.read_text(encoding="utf-8")
    if MARKER in text:
        continue
    if ANCHOR not in text:
        raise RuntimeError(f"Prototype insertion anchor not found in {target}")
    target.write_text(text.replace(ANCHOR, BLOCK + ANCHOR, 1), encoding="utf-8")
    print(f"Applied UI prototype to {target}")
