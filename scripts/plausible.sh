#!/bin/bash

SEARCH_DIR="site"

OLD_STRING="assets/external/plausible.io/js/plausible.js"
NEW_STRING="https://plausible.io/js/plausible.js"

PRECONNECT_LINK='<link rel="preconnect" href="https://plausible.io">'

find "$SEARCH_DIR" -type f -name "*.html" | while read -r file; do
  file_content=$(cat "$file")

  file_content=$(sed "s|$OLD_STRING|$NEW_STRING|g" <<< "$file_content")
  
  file_content=$(sed '/<script/i '$PRECONNECT_LINK' <<< "$file_content")

  echo "$file_content" > "$file"
done