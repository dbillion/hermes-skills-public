#!/usr/bin/awk -f
# Email filtering script for morning brief
# Filters GWS Gmail +triage output for urgent emails
# Usage: gws gmail +triage | tail -n +3 | awk -f email_filtering.awk

BEGIN {
    FS = "[[:space:]]{2,}"  # Split on 2 or more spaces
    # Keywords to match (case insensitive)
    keywords = "recruiter|deadline|invoice|urgent|important|offer|interview|application|signup|debt|earning"
}

NR >= 3 {
    from = $2
    subject = $4
    # Combine remaining fields into subject
    for (i = 5; i <= NF; i++) {
        subject = subject " " $i
    }
    combined = tolower(from " " subject)
    
    # Check if any keyword matches
    if (combined ~ keywords) {
        # Clean from address (remove <> if present)
        gsub(/[<>]/, "", from)
        print from ": " subject
    }
}