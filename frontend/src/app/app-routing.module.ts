import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { CameraComponent } from './camera/camera.component';
import { TodayAttendanceComponent } from './today-attendance/today-attendance.component';
import { EmployeeSelectionComponent } from './employee-selection/employee-selection.component';
import { EmployeeRegisterComponent } from './employee-register/employee-register.component';

const routes: Routes = [
  { path: 'camera', component: CameraComponent },
  { path: 'today-attendance', component: TodayAttendanceComponent },
  { path: 'employee-attendance', component: EmployeeSelectionComponent },
  { path: 'register-employee', component: EmployeeRegisterComponent },
  { path: '', redirectTo: '/camera', pathMatch: 'full' }, // Default route
  { path: '**', redirectTo: '/camera' } // Fallback for undefined routes
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
