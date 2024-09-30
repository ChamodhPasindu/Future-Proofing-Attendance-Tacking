import { Component, ElementRef, ViewChild } from '@angular/core';
import { AttendanceService } from '../attendance.service';
import { ToastrService } from 'ngx-toastr';

@Component({
  selector: 'app-camera',
  templateUrl: './camera.component.html',
  styleUrls: ['./camera.component.scss'],
})
export class CameraComponent {
  @ViewChild('video', { static: false }) video!: ElementRef;
  capturedImage: any = null;
  selectedEmployee: any;
  isCameraEnabled: boolean = false;

  constructor(
    private service: AttendanceService,
    private toastr: ToastrService
  ) {}

  enableCamera() {
    this.isCameraEnabled = true;
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      navigator.mediaDevices.getUserMedia({ video: true }).then((stream) => {
        this.video.nativeElement.srcObject = stream;
        this.video.nativeElement.play();
      });
    }
  }

  disableCamera() {
    this.isCameraEnabled = false;
    const videoElement = this.video.nativeElement;
  
    const stream = videoElement.srcObject as MediaStream;
  
    if (stream) {
      const tracks = stream.getTracks();
      tracks.forEach(track => track.stop()); 
    }
  
    videoElement.srcObject = null;
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
          this.toastr.success('Employee Identified', 'Success');
        },
        error: (err) => {
          this.toastr.error(
            'System cannot identified you.Please Try Again!',
            'Cannot Recognize'
          );
        },
      });
    } else {
      this.toastr.warning('', 'Image not Captured');
    }
  }
}
