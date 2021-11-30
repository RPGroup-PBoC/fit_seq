using CSV, DataFrames, XLSX, CairoMakie, Jedi, ColorSchemes, Statistics

CairoMakie.activate!()
# Set Style
Jedi.styles.default_makie!()

sequential_cmaps = [
    "Blues",
    "Reds",
    "Greens",
    "Oranges",
    "Purples",
]


##
# Find home directory
dir = @__DIR__
home_dir = joinpath(split(dir, '/')[1:end-4]...)

# Find date
workdir = split(dir, '/')[end]
DATE = parse(Int64, split(workdir, '_')[1])
RUN_NO = parse(Int64, split(workdir, '_')[2][end])
##

# Load the data.
file = "/$(home_dir)/data/plate_reader/$workdir.txt"

xf = XLSX.readxlsx(dir * "/$(DATE)_plate_layout.xlsx")

# see all sheet names
layout = XLSX.sheetnames(xf)

# Read layout information
layout_info = DataFrames.DataFrame()
# Loop through layout info
for table in layout
    flattened = vec(hcat(XLSX.getdata(xf[table])...))
    DataFrames.insertcols!(layout_info, table => flattened)
end

# Define rows and columns read on plate
DataFrames.insertcols!(layout_info, "row" => [x[1] for x in layout_info[!, "well"]])
DataFrames.insertcols!(layout_info, "col" => [x[2:end] for x in layout_info[!, "well"]])

##
# Initialize plot

fig = Figure(resolution=(900, 300 * ((length(layout) + 1) ÷ 2)))


# Loop through features
i=0
for feature in layout
    cmap = rand(sequential_cmaps)
    
    # If well, don't add information
    if (feature == "well")
        continue
    end
    i += 1

    println(feature)
    ax = Axis(fig[(i-1) ÷ 2 + 1, ((i-1) % 2) + 1 ])
    # Extract strain data and pivot dataframe to obtain proper dimensions
    data = layout_info[!, ["row", "col", feature]]
    # Add code for categorical data
    cat_dict = Dict(unique(data[!, feature]) .=> collect(1:length(unique(data[!, feature]))))
    data[!, "feature_code"] = [cat_dict[x] for x in data[!, feature]]
    row_dict = Dict(unique(data[!, "row"]) .=> collect(1:length(unique(data[!, "row"]))))
    data[!, "row_code"] = [row_dict[x] for x in data[!, "row"]]
    col_dict = Dict(unique(data[!, "col"]) .=> collect(1:length(unique(data[!, "col"]))))
    data[!, "col_code"] = [col_dict[x] for x in data[!, "col"]]

    # Pivot dataframe for both code and label to generate heatmap
    cmap = colorschemes[Symbol("$(sequential_cmaps[i])_$(max(3, length(unique(data.feature_code))))")]

    # Generate colormap
    heatmap!(ax, data.col_code, data.row_code, data.feature_code, strokewidth = 1, strokecolor="black", colormap=cmap)
    text!(ax, data[!, feature], position = Point.(data.col_code, data.row_code), align = (:center, :center),
    offset = (0, 0), color = :black, textsize=3)
    # Set plot title
    ax.title = feature
    ax.xgridcolor="white"
    ax.ygridcolor="white"
    ax.xgridwidth=5
    ax.xticks=(collect(1:12), string.(collect(1:12)))
    ax.yticks=(collect(1:8), ["A", "B", "C", "D", "E", "F", "G", "H"])
    ax.yreversed = true
end


# Save it to the output file
if ~ispath("$dir/output")  # Check if directyr exists
    mkdir("$dir/output")  # Generate directory if required
end
fig
save("$dir/output/plate_layout.pdf", fig)