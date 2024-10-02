#!/bin/bash

SEARCH_DIR="site"

OLD_STRING="assets/external/plausible.io/js/plausible.js"
NEW_STRING="https://plausible.io/js/plausible.js"

PRECONNECT_LINK='<link rel="preconnect" href="https://plausible.io">'

find "$SEARCH_DIR" -type f -name "*.html" | while read -r html_file; do
    if grep -q "$OLD_STRING" "$html_file"; then
        echo "Updating $html_file"

        sed -i "s|$OLD_STRING|$NEW_STRING|g" "$html_file"

        sed -i "/<script[^>]*src=\"$NEW_STRING\"/i\\
$PRECONNECT_LINK
" "$html_file"
    fi
done
