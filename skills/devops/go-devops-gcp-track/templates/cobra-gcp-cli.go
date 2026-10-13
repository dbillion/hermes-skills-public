// TEMPLATE: skeleton for a Go DevOps CLI that shells out to gcloud via sh().
// Copy, rename, and fill in the deploy() body per project. The sh() helper is
// mandatory — spawned shells don't inherit the login PATH where gcloud lives.

package main

import (
	"fmt"
	"os"
	"os/exec"
	"strings"

	"github.com/spf13/cobra"
)

// deployFlag, projectFlag, etc. set by cobra flags.

func main() {
	root := &cobra.Command{
		Use:   "<functionname>",
		Short: "<one-line: the problem this solves> (Go/GCP DevOps track)",
		RunE:  run,
	}
	root.Flags().StringVar(&projectFlag, "project", "future-abode-338616", "GCP project")
	root.Flags().BoolVarP(&deployFlag, "deploy", "d", false, "run cloud create+verify+teardown")
	// add per-project flags...
	if err := root.Execute(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}

func run(cmd *cobra.Command, args []string) error {
	// local work (build/test) here; if deployFlag { return deploy() }
	return nil
}

// sh runs a shell command with the GCloud SDK on PATH. MANDATORY for gcloud.
func sh(c string) (string, error) {
	cmd := exec.Command("/bin/sh", "-c",
		"export PATH=$PATH:/home/deeone/google-cloud-sdk/bin && "+c)
	b, err := cmd.CombinedOutput()
	return string(b), err
}

// deploy pattern: always destroy on exit, even on error.
func deploy() error {
	proj := projectFlag
	var firstErr error
	steps := []string{
		// "cd <outDir> && terraform init -input=false",
		// "cd <outDir> && terraform apply -auto-approve -var project="+proj,
		// "gcloud ... create/verify ...",
		// "cd <outDir> && terraform destroy -auto-approve -var project="+proj,
	}
	for _, c := range steps {
		full := "export PATH=$PATH:/home/deeone/google-cloud-sdk/bin && export GOOGLE_CLOUD_PROJECT=" + proj + " && " + c
		fmt.Printf("$ %s\n", c)
		out, err := sh(full)
		fmt.Println(out)
		if err != nil && firstErr == nil {
			firstErr = fmt.Errorf("step failed: %w", err)
		}
	}
	if firstErr != nil {
		return firstErr
	}
	return nil
}

var (
	projectFlag string
	deployFlag  bool
)

// NOTE: trim pubkey newlines (strings.TrimSpace) before HCL interpolation;
// make firewall/resource names unique per run to avoid 409 orphan collisions.
