# Combine the draw commands for Sound,
# Pitch and TextGrid objects

form Draw annotated Sound and Pitch...
  real left_Time_range_(s)        0
  real right_Time_range_(s)       0 (= all)
  real left_Vertical_range        -0.25
  real right_Vertical_range       0.25 (= auto)
  optionmenu Sound_drawing_method: 1
    option Curve
    option Bars
    option Poles
    option Speckles
  boolean Show_boundaries no
  boolean Use_text_styles yes
  boolean Garnish yes
  comment What proportion of the graph should be used for the Sound?
  positive Figure_ratio 0.55
endform

# Get information on current picture
info$ = Picture info
original_colour.r$ = extractWord$(info$,  "Red:")
original_colour.g$ = extractWord$(info$,  "Green:")
original_colour.b$ = extractWord$(info$,  "Blue:")
picture.line_width = extractNumber(info$, "Line width:")
picture.left       = extractNumber(info$, "Inner viewport left:")
picture.right      = extractNumber(info$, "Inner viewport right:")
picture.top        = extractNumber(info$, "Inner viewport top:")
picture.bottom     = extractNumber(info$, "Inner viewport bottom:")
picture.height     = picture.bottom - picture.top

# Sound options
sound.start   = left_Time_range
sound.end     = right_Time_range
sound.min     = left_Vertical_range
sound.max     = right_Vertical_range
sound.method$ = sound_drawing_method$

# Draw options
fzero.colour$      = "Cyan"
fzero.width        = 2
fzero.border       = 1
fzero.border_width = 2
point.marker_size  = 0.1
precision          = 3

# Identify objects
# If no Pitch object is selected, generate one
sound = selected("Sound")
textgrid = selected("TextGrid")

# Identify ranges for sound
selectObject: sound
if !sound.start and !sound.end
  sound.start = Get start time
  sound.end = Get end time
endif
sound.duration = sound.end - sound.start
if !sound.min and !sound.max
  sound.min = Get minimum: sound.start, sound.end, "None"
  sound.max = Get maximum: sound.start, sound.end, "None"
endif

# Select top of figure, for Sound and Pitch data
Select inner viewport:
  ... picture.left,
  ... picture.right,
  ... picture.top,
  ... picture.top + (picture.height * figure_ratio)

# Draw sound
selectObject: sound
Draw: sound.start, sound.end, sound.min, sound.max, "no", sound.method$

# Extract range from TextGrid object
selectObject: textgrid
textgrid_part = Extract part: sound.start, sound.end, "yes"
total_tiers = Get number of tiers
tier.height = 1 / total_tiers

# Draw boundaries (on Sound and Pitch)
if show_boundaries
  for tier to total_tiers
    interval_tier = Is interval tier: tier
    item$ = if interval_tier then "interval" else "point" fi
    total_items = do("Get number of " + item$ + "s...", tier)
    for item to total_items
      if interval_tier
        time = Get end point: tier, item
      else
        time = Get time of point: tier, item
      endif
      One mark bottom: time, "no", "no", "yes", ""
  endfor
endif

# Return to original colour
Colour: "{" +
  ... original_colour.r$ + "," +
  ... original_colour.g$ + "," +
  ... original_colour.b$ + "}"

if 1 - figure_ratio
  # Select bottom of figure, for TextGrid data
  Select inner viewport:
    ... picture.left,
    ... picture.right,
    ... picture.top + (picture.height * figure_ratio),
    ... picture.bottom

  # Adjust vertical axis
  Axes: sound.start, sound.end, 1, 0


# Select the full viewport
Select inner viewport:
  ... picture.left,
  ... picture.right,
  ... picture.top,
  ... picture.bottom

# Finish garnish
  Draw inner box
  One mark bottom: sound.start, "no", "yes", "no", fixed$(sound.start, precision)
  One mark bottom: sound.end,   "no", "yes", "no", fixed$(sound.end,   precision)
  Text bottom: "yes", "Time (s)"

# Re-select original objects
selectObject: sound, textgrid

#configured to draw text with 4 inch height and 0.55 ratio

Select outer viewport: 0.4, 1.4, 1, 1.5
Text: 0, "centre", 0, "Half", "Audio waveform of"
Text special: 0, "Centre", 1.5, "Half", "Times", 10, "0", "voice #1 and #2 mixed"

Select outer viewport: 0.3, 1.3, 2, 2.5
Text bottom: "yes", "Voice #1 alignment"

Select outer viewport: 0.3, 1.3, 2.5, 3
Text bottom: "yes", "Voice #2 alignment"

Select outer viewport: 0.3, 1.3, 3, 3.5
Text bottom: "yes", "Predicted alignment"
