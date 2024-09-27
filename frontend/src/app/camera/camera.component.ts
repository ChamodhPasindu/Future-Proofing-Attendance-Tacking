import { Component, ElementRef, ViewChild } from '@angular/core';
import { AttendanceService } from '../attendance.service';

@Component({
  selector: 'app-camera',
  templateUrl: './camera.component.html',
  styleUrls: ['./camera.component.scss'],
})
export class CameraComponent {
  @ViewChild('video', { static: false }) video!: ElementRef;
  capturedImage: any = null;
  selectedEmployee:any;

  constructor(private service: AttendanceService) {}

  enableCamera() {
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      navigator.mediaDevices.getUserMedia({ video: true }).then((stream) => {
        this.video.nativeElement.srcObject = stream;
        this.video.nativeElement.play();
      });
    }
  }

  capture() {
    const canvas = document.createElement('canvas');
    canvas.width = this.video.nativeElement.videoWidth;
    canvas.height = this.video.nativeElement.videoHeight;
    const ctx = canvas.getContext('2d');
    if (ctx) {
      ctx.drawImage(
        this.video.nativeElement,
        0,
        0,
        canvas.width,
        canvas.height
      );
      this.capturedImage = canvas.toDataURL('image/png'); // Convert the captured image to Base64
      this.recognizeCustomer();
    }
  }

  recognizeCustomer() {
    if (this.capturedImage) {
      const imageFile = this.service.dataURItoFile(
        this.capturedImage,
        'captured-image.png'
      );

      this.service.recognizeCustomer(imageFile).subscribe({
        next: (res) => {
          console.log('Recognition successful:', res);
          this.selectedEmployee = res.data; 
        },
        error: (err) => {
          console.error('Error during recognition:', err);
        },
      });
    } else {
      console.error('No image captured for recognition.');
    }
  }
}
