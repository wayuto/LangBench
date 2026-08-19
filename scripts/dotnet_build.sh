#!/usr/bin/env bash
# scripts/dotnet_build.sh
# 为单个 C#/VB 源文件生成临时 .NET 项目并编译
# 用法: dotnet_build.sh <cs|vb> <output> <source_file>...
set -euo pipefail

LANG_KIND=$1; shift
OUTPUT=$1; shift

NAME=$(basename "$OUTPUT")
OUT_DIR=$(dirname "$OUTPUT")
DIR="/tmp/langbench/dotnet/${LANG_KIND}-${NAME}"

rm -rf "$DIR"
mkdir -p "$DIR"
cp "$@" "$DIR"/

if [ "$LANG_KIND" = "vb" ]; then
    EXT="vbproj"
else
    EXT="csproj"
fi

cat > "$DIR/$NAME.$EXT" <<EOF
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net8.0</TargetFramework>
    <AssemblyName>$NAME</AssemblyName>
    <Nullable>disable</Nullable>
    <ImplicitUsings>disable</ImplicitUsings>
    <InvariantGlobalization>true</InvariantGlobalization>
  </PropertyGroup>
</Project>
EOF

dotnet build "$DIR/$NAME.$EXT" -c Release -o "$OUT_DIR" --nologo -v q