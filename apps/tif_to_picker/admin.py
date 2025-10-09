# In your admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
import os
import threading
import time
from .models import Mockup

@admin.register(Mockup)
class MockupAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'has_base64_image', 'image_preview', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['image_preview_large', 'image_base64_info']
    
    def has_base64_image(self, obj):
        return bool(obj.image_base64)
    has_base64_image.boolean = True
    has_base64_image.short_description = 'Has Base64'
    
    def image_preview(self, obj):
        if obj.image_base64:
            return format_html(
                '<img src="data:{};base64,{}" style="max-width: 50px; max-height: 50px;" />',
                obj.image_type,
                obj.image_base64[:100] + '...'  # Truncate for performance
            )
        return "No image"
    image_preview.short_description = 'Preview'
    
    def image_preview_large(self, obj):
        if obj.image_base64:
            return format_html(
                '<img src="data:{};base64,{}" style="max-width: 200px; max-height: 200px;" />',
                obj.image_type,
                obj.image_base64
            )
        return "No image"
    image_preview_large.short_description = 'Image Preview'
    
    def image_base64_info(self, obj):
        if obj.image_base64:
            size_kb = len(obj.image_base64) * 3 / 4 / 1024  # Approximate size in KB
            return f"Type: {obj.image_type}, Size: ~{size_kb:.1f} KB"
        return "No base64 data"
    image_base64_info.short_description = 'Base64 Info'
    
    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


# ===== Custom Admin Utility: Dataset Manager =====
def _ensure_dataset_dirs():
    base_dir = os.path.join(settings.MEDIA_ROOT, 'dataset')
    gradient_dir = os.path.join(base_dir, 'gradient')
    normal_dir = os.path.join(base_dir, 'normal')
    os.makedirs(gradient_dir, exist_ok=True)
    os.makedirs(normal_dir, exist_ok=True)
    return base_dir, gradient_dir, normal_dir


@admin.site.admin_view
@require_http_methods(["GET", "POST"])
def dataset_manager_view(request):
    base_dir, gradient_dir, normal_dir = _ensure_dataset_dirs()

    if request.method == 'POST':
        action = request.POST.get('action', 'upload')
        if action == 'upload':
            target_class = request.POST.get('class')  # 'gradient' or 'normal'
            files = request.FILES.getlist('images')
            if target_class not in ['gradient', 'normal']:
                messages.error(request, 'Invalid class selected')
                return redirect(request.path)
            if not files:
                messages.error(request, 'No files uploaded')
                return redirect(request.path)
            target_dir = gradient_dir if target_class == 'gradient' else normal_dir
            uploaded = 0
            for file_obj in files:
                save_path = os.path.join(target_dir, file_obj.name)
                # Avoid overwrite by adding counter
                if os.path.exists(save_path):
                    name, ext = os.path.splitext(file_obj.name)
                    counter = 1
                    while os.path.exists(save_path):
                        save_path = os.path.join(target_dir, f"{name}_{counter}{ext}")
                        counter += 1
                with open(save_path, 'wb+') as dest:
                    for chunk in file_obj.chunks():
                        dest.write(chunk)
                uploaded += 1
            messages.success(request, f'Uploaded {uploaded} file(s) to {target_class}/')
            return redirect(request.path)
        elif action == 'delete':
            rel_path = request.POST.get('rel_path')  # e.g., dataset/gradient/file.png
            if not rel_path:
                messages.error(request, 'Missing file path')
                return redirect(request.path)
            abs_path = os.path.join(settings.MEDIA_ROOT, rel_path.replace('/', os.sep))
            # Safety: ensure path is within MEDIA_ROOT/dataset
            if not abs_path.startswith(os.path.join(settings.MEDIA_ROOT, 'dataset')):
                messages.error(request, 'Invalid file path')
                return redirect(request.path)
            try:
                if os.path.exists(abs_path):
                    os.remove(abs_path)
                    messages.success(request, f'Deleted: {rel_path}')
                else:
                    messages.warning(request, 'File not found')
            except Exception as exc:
                messages.error(request, f'Error deleting file: {exc}')
            return redirect(request.path)
        elif action == 'train':
            # Start training in background if not already running
            lock_path = os.path.join(settings.BASE_DIR, 'training.lock')
            if os.path.exists(lock_path):
                messages.warning(request, 'Training is already running')
                return redirect(request.path)
            data_dir = os.path.join(settings.MEDIA_ROOT, 'dataset')
            def training_task():
                # Create lock
                with open(lock_path, 'w') as f:
                    f.write(str(time.time()))
                try:
                    run_training(data_dir)
                except Exception as e:
                    # Log and continue
                    print(f"Training error: {e}")
                finally:
                    try:
                        if os.path.exists(lock_path):
                            os.remove(lock_path)
                        # Mark progress as complete
                        progress_path = os.path.join(settings.BASE_DIR, 'training_progress.json')
                        try:
                            import json
                            with open(progress_path, 'r') as pf:
                                prog = json.load(pf)
                        except Exception:
                            prog = {}
                        prog['status'] = 'idle'
                        prog['updated_at'] = time.time()
                        with open(progress_path, 'w') as pf:
                            json.dump(prog, pf)
                        # Remove stop flag if present
                        stop_flag = os.path.join(settings.BASE_DIR, 'training.stop')
                        if os.path.exists(stop_flag):
                            os.remove(stop_flag)
                    except Exception:
                        pass
            threading.Thread(target=training_task, daemon=True).start()
            messages.success(request, 'Training started in background')
            return redirect(request.path)
        elif action == 'stop':
            # Signal training to stop via flag
            lock_path = os.path.join(settings.BASE_DIR, 'training.lock')
            if not os.path.exists(lock_path):
                messages.info(request, 'No training is running')
                return redirect(request.path)
            stop_flag = os.path.join(settings.BASE_DIR, 'training.stop')
            try:
                with open(stop_flag, 'w') as f:
                    f.write('1')
                # Update progress status
                try:
                    import json
                    progress_path = os.path.join(settings.BASE_DIR, 'training_progress.json')
                    with open(progress_path, 'r') as pf:
                        prog = json.load(pf)
                except Exception:
                    prog = {}
                prog['status'] = 'stopping'
                prog['updated_at'] = time.time()
                with open(progress_path, 'w') as pf:
                    json.dump(prog, pf)
                messages.success(request, 'Stop signal sent. Training will stop after current batch.')
            except Exception as exc:
                messages.error(request, f'Could not signal stop: {exc}')
            return redirect(request.path)

    # GET: list files
    def list_files(dir_path, class_name):
        items = []
        if os.path.exists(dir_path):
            for fname in sorted(os.listdir(dir_path)):
                if fname.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    rel = os.path.join('dataset', class_name, fname).replace('\\', '/')
                    items.append({
                        'name': fname,
                        'rel_path': rel,
                        'url': settings.MEDIA_URL + rel
                    })
        return items

    gradient_files = list_files(gradient_dir, 'gradient')
    normal_files = list_files(normal_dir, 'normal')

    # Training status/info
    lock_path = os.path.join(settings.BASE_DIR, 'training.lock')
    model_path = os.path.join(settings.BASE_DIR, 'best_resnet_model.pth')
    progress_path = os.path.join(settings.BASE_DIR, 'training_progress.json')
    stop_flag_path = os.path.join(settings.BASE_DIR, 'training.stop')

    # Load progress
    progress = None
    if os.path.exists(progress_path):
        try:
            import json
            with open(progress_path, 'r') as pf:
                progress = json.load(pf)
        except Exception:
            progress = None

    # Heal stale state quickly: if lock exists but looks stale (older than 60s),
    # or progress says not running, or progress is stale (>60s), clear lock/stop
    if os.path.exists(lock_path):
        try:
            lock_age = time.time() - os.path.getmtime(lock_path)
        except Exception:
            lock_age = 999999
        progress_status = progress.get('status') if isinstance(progress, dict) else None
        try:
            progress_age = time.time() - float(progress.get('updated_at')) if progress and progress.get('updated_at') else 999999
        except Exception:
            progress_age = 999999
        if (progress_status and progress_status != 'running') or lock_age > 60 or progress_age > 60:
            try:
                os.remove(lock_path)
            except Exception:
                pass
            try:
                if os.path.exists(stop_flag_path):
                    os.remove(stop_flag_path)
            except Exception:
                pass

    training_running = os.path.exists(lock_path)
    model_info = None
    if os.path.exists(model_path):
        try:
            mtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(model_path)))
            size_mb = os.path.getsize(model_path) / (1024 * 1024)
            model_info = {
                'mtime': mtime,
                'size_mb': f"{size_mb:.2f}"
            }
        except Exception:
            pass

    context = {
        'title': 'Dataset Manager',
        'gradient_files': gradient_files,
        'normal_files': normal_files,
        'training_running': training_running,
        'model_info': model_info,
        'progress': progress,
    }
    return render(request, 'admin/dataset_manager.html', context)


def get_admin_urls(original_get_urls):
    def urls():
        custom_urls = [
            path('dataset-manager/', dataset_manager_view, name='admin-dataset-manager'),
            path('dataset-manager/progress/', dataset_training_progress, name='admin-dataset-progress'),
        ]
        return custom_urls + original_get_urls()
    return urls


# Inject our custom URL into admin
admin.site.get_urls = get_admin_urls(admin.site.get_urls)


# ===== Training Implementation (background) =====
def run_training(data_dir):
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader, Dataset
    from torchvision import transforms, models
    from PIL import Image
    import os
    import numpy as np

    class ImageDataset(Dataset):
        def __init__(self, root_dir, transform=None):
            self.root_dir = root_dir
            self.transform = transform
            self.images = []
            self.labels = []
            classes = ['gradient', 'normal']
            for class_idx, class_name in enumerate(classes):
                class_path = os.path.join(root_dir, class_name)
                if os.path.exists(class_path):
                    for img_name in os.listdir(class_path):
                        if img_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                            self.images.append(os.path.join(class_path, img_name))
                            self.labels.append(class_idx)

        def __len__(self):
            return len(self.images)

        def __getitem__(self, idx):
            image_path = self.images[idx]
            image = Image.open(image_path).convert('RGB')
            label = self.labels[idx]
            if self.transform:
                image = self.transform(image)
            return image, label

    class ResNetClassifier(nn.Module):
        def __init__(self, num_classes=2, pretrained=True, resnet_type='resnet50'):
            super(ResNetClassifier, self).__init__()
            if resnet_type == 'resnet18':
                self.backbone = models.resnet18(pretrained=pretrained)
                num_features = 512
            elif resnet_type == 'resnet34':
                self.backbone = models.resnet34(pretrained=pretrained)
                num_features = 512
            elif resnet_type == 'resnet50':
                self.backbone = models.resnet50(pretrained=pretrained)
                num_features = 2048
            elif resnet_type == 'resnet101':
                self.backbone = models.resnet101(pretrained=pretrained)
                num_features = 2048
            elif resnet_type == 'resnet152':
                self.backbone = models.resnet152(pretrained=pretrained)
                num_features = 2048
            else:
                raise ValueError(f"Unsupported ResNet type: {resnet_type}")
            self.backbone.fc = nn.Sequential(
                nn.Dropout(0.5),
                nn.Linear(num_features, 512),
                nn.ReLU(inplace=True),
                nn.Dropout(0.3),
                nn.Linear(512, 256),
                nn.ReLU(inplace=True),
                nn.Dropout(0.2),
                nn.Linear(256, num_classes)
            )

        def forward(self, x):
            return self.backbone(x)

    class ImageClassifier:
        def __init__(self, data_dir, img_size=224, batch_size=16, resnet_type='resnet50', pretrained=True):
            self.data_dir = data_dir
            self.img_size = img_size
            self.batch_size = batch_size
            self.resnet_type = resnet_type
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            print(f"Using device: {self.device}")
            print(f"Using {resnet_type} architecture")
            self.model = ResNetClassifier(num_classes=2, pretrained=pretrained, resnet_type=resnet_type).to(self.device)
            self.criterion = nn.CrossEntropyLoss()
            if pretrained:
                backbone_params = []
                classifier_params = []
                for name, param in self.model.named_parameters():
                    if 'backbone.fc' in name:
                        classifier_params.append(param)
                    else:
                        backbone_params.append(param)
                self.optimizer = optim.Adam([
                    {'params': backbone_params, 'lr': 0.0001},
                    {'params': classifier_params, 'lr': 0.001}
                ])
            else:
                self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
            self.scheduler = optim.lr_scheduler.StepLR(self.optimizer, step_size=10, gamma=0.1)
            self.train_losses = []
            self.train_accs = []

        def get_data_loader(self):
            train_transform = transforms.Compose([
                transforms.Resize((self.img_size, self.img_size)),
                transforms.RandomHorizontalFlip(p=0.5),
                transforms.RandomVerticalFlip(p=0.3),
                transforms.RandomRotation(degrees=20),
                transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1),
                transforms.RandomAffine(degrees=0, translate=(0.1, 0.1), scale=(0.9, 1.1)),
                transforms.RandomPerspective(distortion_scale=0.1, p=0.2),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
            train_dataset = ImageDataset(self.data_dir, transform=train_transform)
            train_loader = DataLoader(train_dataset, batch_size=self.batch_size, shuffle=True, num_workers=0, pin_memory=True)
            print(f"Training on {len(train_dataset)} images")
            return train_loader

        def train_epoch(self, train_loader):
            self.model.train()
            running_loss = 0.0
            correct = 0
            total = 0
            stop_flag = os.path.join(settings.BASE_DIR, 'training.stop')
            for batch_idx, (images, labels) in enumerate(train_loader):
                # Check for stop signal
                if os.path.exists(stop_flag):
                    print('Stop signal detected. Interrupting training loop...')
                    self._stop = True
                    break
                images, labels = images.to(self.device, non_blocking=True), labels.to(self.device, non_blocking=True)
                self.optimizer.zero_grad()
                outputs = self.model(images)
                loss = self.criterion(outputs, labels)
                loss.backward()
                self.optimizer.step()
                running_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
                if (batch_idx + 1) % 10 == 0:
                    print(f'Batch [{batch_idx+1}/{len(train_loader)}], Loss: {loss.item():.4f}')
            epoch_loss = running_loss / max(1, len(train_loader))
            epoch_acc = 100 * correct / max(1, total)
            return epoch_loss, epoch_acc

        def train(self, num_epochs=30):
            train_loader = self.get_data_loader()
            best_train_acc = 0.0
            patience = 8
            patience_counter = 0
            print(f"Starting training for {num_epochs} epochs...")
            print(f"Total batches per epoch: {len(train_loader)}")
            best_model_path = os.path.join(settings.BASE_DIR, 'best_resnet_model.pth')
            progress_path = os.path.join(settings.BASE_DIR, 'training_progress.json')
            # initialize progress file
            try:
                import json
                with open(progress_path, 'w') as pf:
                    json.dump({
                        'status': 'running',
                        'epoch': 0,
                        'num_epochs': num_epochs,
                        'train_loss': None,
                        'train_acc': None,
                        'best_acc': 0.0,
                        'updated_at': time.time()
                    }, pf)
            except Exception:
                pass
            # Remove any stale stop flag
            try:
                stop_flag = os.path.join(settings.BASE_DIR, 'training.stop')
                if os.path.exists(stop_flag):
                    os.remove(stop_flag)
            except Exception:
                pass
            self._stop = False
            for epoch in range(num_epochs):
                print(f'\nEpoch [{epoch+1}/{num_epochs}]')
                train_loss, train_acc = self.train_epoch(train_loader)
                self.train_losses.append(train_loss)
                self.train_accs.append(train_acc)
                print(f'Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}%')
                print(f'Learning Rate: {self.optimizer.param_groups[0]["lr"]:.6f}')
                print('-' * 60)
                if getattr(self, '_stop', False):
                    print('Training stopped by user.')
                    break
                if train_acc > best_train_acc:
                    best_train_acc = train_acc
                    patience_counter = 0
                    torch.save(self.model.state_dict(), best_model_path)
                    print(f'New best model saved! Accuracy: {best_train_acc:.2f}%')
                else:
                    patience_counter += 1
                    if patience_counter >= patience:
                        print(f'Early stopping at epoch {epoch+1}')
                        break
                self.scheduler.step()
                # write progress
                try:
                    import json
                    with open(progress_path, 'w') as pf:
                        json.dump({
                            'status': 'running' if not getattr(self, '_stop', False) else 'stopping',
                            'epoch': epoch + 1,
                            'num_epochs': num_epochs,
                            'train_loss': float(train_loss),
                            'train_acc': float(train_acc),
                            'best_acc': float(best_train_acc),
                            'updated_at': time.time()
                        }, pf)
                except Exception:
                    pass
            # Load best model
            if os.path.exists(best_model_path):
                self.model.load_state_dict(torch.load(best_model_path, map_location=self.device))
            print(f'\nTraining completed!')
            print(f'Best training accuracy: {best_train_acc:.2f}%')

    # Execute training
    classifier = ImageClassifier(data_dir, img_size=224, batch_size=16, resnet_type='resnet50', pretrained=True)
    classifier.train(num_epochs=30)


@admin.site.admin_view
def dataset_training_progress(request):
    import json
    progress_path = os.path.join(settings.BASE_DIR, 'training_progress.json')
    if os.path.exists(progress_path):
        try:
            with open(progress_path, 'r') as pf:
                data = json.load(pf)
        except Exception:
            data = { 'status': 'unknown' }
    else:
        data = { 'status': 'idle' }
    from django.http import JsonResponse
    return JsonResponse(data)

