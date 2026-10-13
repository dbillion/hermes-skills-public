package main

import (
	"fmt"
	"os"
	"runtime"

	"github.com/spf13/cobra"
)

// Template: a roadmap.sh-style DevOps CLI in Go (cobra + OS-aware guards).
// Copy, rename the command to a FUNCTIONAL name (sysstats, logarc, nginxlog...), add your logic.
// Install with `go build -o $HOME/go/bin/<funcname> .`  (NOT `go install .` — that names the
// binary after the directory, ignoring Use).

var (
	statFlag   string
	formatFlag string
)

func main() {
	root := &cobra.Command{
		Use:   "funcname", // <-- functional name the tool solves, NOT bN
		Short: "<one-line description of what this tool does>",
		Run: func(cmd *cobra.Command, args []string) {
			// OS-aware guard example:
			if runtime.GOOS != "linux" && statFlag == "load" {
				fmt.Println("load: n/a on", runtime.GOOS)
				return
			}
			fmt.Printf("stat=%s format=%s os=%s\n", statFlag, formatFlag, runtime.GOOS)
		},
	}
	root.Flags().StringVarP(&statFlag, "stat", "s", "all", "what to report")
	root.Flags().StringVarP(&formatFlag, "format", "f", "text", "text|json")

	if err := root.Execute(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
