import { Component, ElementRef, OnInit, ViewChild } from '@angular/core';
import { AttendanceService } from '../attendance.service';

@Component({
  selector: 'app-employee-register',
  templateUrl: './employee-register.component.html',
  styleUrls: ['./employee-register.component.scss'],
})
export class EmployeeRegisterComponent implements OnInit {
  @ViewChild('video', { static: false }) video!: ElementRef;
  capturedImage: any = null;
  selectedEmployee: any = null;
  employees: any[] = [];

  constructor(private service: AttendanceService) {}

  ngOnInit(): void {
    this.service.getAllEmployees().subscribe({
      next: (res) => {
        this.employees = res.data;
      },
      error: (err) => {
        console.log(err);
      },
    });
  }

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
    }
  }

  // Submit form
  submitForm() {
    if (this.selectedEmployee && this.capturedImage) {
      const imageFile = this.service.dataURItoFile(
        this.capturedImage,
        `${this.selectedEmployee.name}.png`
      );

      this.service
        .registerCustomer(
          imageFile,
          this.selectedEmployee.tag,
          this.selectedEmployee.name
        )
        .subscribe({
          next: (res) => {
            console.log(res);
          },
          error: (err) => {
            console.log(err);
          },
        });
    } else {
      console.error('Please select an employee and capture an image.');
    }
  }
}
