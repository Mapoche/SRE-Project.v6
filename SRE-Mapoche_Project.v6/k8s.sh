
#!/bin/bash
set -e

MANIFEST_DIR="./"

echo "🚀 Applying all Kubernetes manifests except Ansible playbooks..."
for file in "$MANIFEST_DIR"/*.yaml; do
    case "$file" in
        *iac_playbook.yaml|*playbook.yaml|*master_playbook.yaml)
            echo "⏭ Skipping $file"
            ;;
        *)
            # Check if file contains apiVersion and kind
            if ! grep -q 'apiVersion:' "$file" || ! grep -q 'kind:' "$file"; then
                echo "⏭ Skipping non-Kubernetes file: $file"
                continue
            fi

            ns=$(grep -m1 'namespace:' "$file" | awk '{print $2}')
            if [ -n "$ns" ]; then
                echo "🔍 Namespace detected: $ns"
                kubectl get ns "$ns" >/dev/null 2>&1 || kubectl create ns "$ns"
            fi
            echo "📄 Applying $file"
            kubectl apply -f "$file"
            ;;
    esac
done

echo "✅ All manifests applied successfully!"
