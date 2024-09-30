import { Component, ElementRef, OnInit, ViewChild } from '@angular/core';
import { AttendanceService } from '../attendance.service';
import { ToastrService } from 'ngx-toastr';

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
  isCameraEnabled: boolean = false;

  constructor(private service: AttendanceService,private toastr: ToastrService) {}

  ngOnInit(): void {
    this.service.getAllEmployees().subscribe({
      next: (res) => {
        if(!res.data.length){
          this.toastr.error('No any employee record found','Empty Results');
          return;
        }
        this.employees = res.data;
      },
      error: (err) => {
        this.toastr.error('Oops,Something went wrong','System Error');
      },
    });
  }

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
    }
  }

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
            this.toastr.success( 'Registration Successful','Success');
          },
          error: (err) => {
            this.toastr.error( 'Registration Failed','Error');
          },
        });
    } else {
      this.toastr.warning( 'Please select an employee and capture an image','Details Not Found');
    }
  }
}
